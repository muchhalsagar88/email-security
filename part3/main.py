import sys, os, argparse, string, shlex, subprocess
import atexit
from os.path import basename
from random import Random
from datetime import datetime
from cert import fetch_certificate

# Global variables for index file and certificate file names
INDEX_FILE = os.getcwd()+'/index.db'

# In-memory index
index = {}

parser = argparse.ArgumentParser(prog='email_utils', usage='%(prog)s [options]')
parser.add_argument('--send', nargs=1, type=str, 
 	help='Encrypt and send an email to a Unity ID')
parser.add_argument('--receive', nargs=1, type=str, 
 	help='Receive and decrpyt an email from a Unity ID')
args = parser.parse_args()

def _check_index_for_key(key):
	return key in index

def add_key_to_index(key, path):
	index[key] = {
		'cert': path	
	}

def init_structures():
	_populate_index()

def _populate_index():
	if os.path.exists(INDEX_FILE) and os.path.isfile(INDEX_FILE):
		with open(INDEX_FILE, 'r') as fp:
			for line in fp:
				chunks = line.split()
				index[chunks[0]] = {
					'cert': chunks[1]
				}
			print "Populated email indexing"

def persist_index():
	line = ''
	with open(INDEX_FILE, 'w') as fp:
		for pair in index.items():
			line += str(pair[0]) +' '+ str(pair[1]['cert'])+'\n'
		line = line[:-1]
		fp.seek(0, 0)
		fp.write(line)

atexit.register(persist_index)

def verify_certificate(path):
	cmd = 'openssl verify -verbose -CAfile '+path
	cmd += ' root-ca.crt'

	args = shlex.split(cmd)
	p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	p.wait()
	out, err = p.communicate()
	print "OUTPUT: "+out
	
	if p.returncode is not 0:
		print err
		raise Exception("Could not encrypt the email msg")
	if "OK" in out:
		return True
	return False	

def get_certificate_for_key(key):
	if _check_index_for_key(key):
		return index[key]['cert']
	path = fetch_certificate(key)
	add_key_to_index(key, path)
	return path

def generate_random_key():
	r = Random()
	r.seed(63762)
	rand = ''.join(r.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(32))
	return rand

# Generates a file called msg.txt which has the following email content
def generate_email_msg():
	line = "This email is intended for testing purposes only. This email is sent from srmuchha@ncsu.edu. The current timestamp is: "+str(datetime.now())
	file_name = os.getcwd()+'/msg.txt'
	with open(file_name, 'w') as fp:
		fp.write(line)

def create_n_save_encrypted_msg(key):
	cmd = 'openssl enc -aes-256-cbc -base64 -in msg.txt -k '
	cmd += key
	
	args = shlex.split(cmd)
	p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	p.wait()
	out, err = p.communicate()
		
	if p.returncode is not 0:
		print err
		raise Exception("Could not encrypt the email msg")
	return out

def get_public_key_from_cert(cert_file_name):
	cmd = 'openssl x509 -inform PEM -in '
	cmd += cert_file_name
	cmd += ' -pubkey -noout'
	print cmd
	args = shlex.split(cmd)
	p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	p.wait()
	out, err = p.communicate()
		
	if p.returncode is not 0:
		print err
		raise Exception("Could not extract public key from certificate")
	print out
	path = os.getcwd()+'/to_publickey.pem'
	with open(path, 'w') as fp:
		fp.write(out)
	return path

def encrypt_session_key(session_key, public_key_file):
	with open('temp.file', 'w') as fp:
		fp.write(session_key)

	cmd = 'openssl rsautl -in temp.file -out encrypted_key.bin -inkey '
	cmd += public_key_file
	cmd += ' -pubin -encrypt'

	args = shlex.split(cmd)
	p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	p.wait()
	out, err = p.communicate()

	if p.returncode is not 0:
		print err
		raise Exception("Could not encrypt the session key")

def collate_msg(source, to, msg_file_name, enc_key_file_name):
	msg = 'from: '+source+', to: '+to+'\n'
	msg += '-----BEGIN CSC574 MESSAGE-----'
	with open(enc_key_file_name, 'r') as fp:
		msg += fp.read()
	msg += '\n\n'
	with open(msg_file_name, 'r') as fp:
		msg += fp.read()
	msg += '\n'

	with open('msg.txt', 'w') as fp:
		fp.write(msg)

def calculate_hash(msg_file_name, personal_priv_key_file):
	cmd = 'openssl dgst -sha1 -sign '+personal_priv_key_file
	cmd += ' -out signature.sha1 '
	cmd += msg_file_name

	args = shlex.split(cmd)
	p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	p.wait()
	out, err = p.communicate()

	if p.returncode is not 0:
		print err
		raise Exception("Could not calculate hash")

def complete_msg(message_file_name):
	calculate_hash(message_file_name, 'my_private_key.pem') 
	content = None
	with open('signature.sha1', 'rb') as fp:
		content = fp.read()
	rest_of_msg = content + '\n'
	rest_of_msg += '-----END CSC574 MESSAGE-----'
	with open('msg.txt', 'a') as fp:
		fp.write(rest_of_msg)


FROM_ADDRESS = 'srmuchha@ncsu.edu'

def send_email(to):
	to_unity_id = to.split('@')[0]
	session_key = generate_random_key()
	generate_email_msg()
	encrypted_txt = create_n_save_encrypted_msg(session_key)
	with open('msg.txt', 'w') as fp:
		fp.write(encrypted_txt)

	to_cert_name = get_certificate_for_key(to_unity_id)
	# Verify the certificate
	if not verify_certificate(to_cert_name):
		raise Exception("Certificate not valid: "+to_cert_name)
	pub_key_file_name = get_public_key_from_cert(to_cert_name)
	encrypt_session_key(session_key, pub_key_file_name)
	collate_msg(FROM_ADDRESS, to, 'msg.txt', 'encrypted_key.bin')
	complete_msg('msg.txt')
	with open('msg.txt', 'r') as fp:
		print fp.read()
	_clean_up()

def _clean_up():
	#os.remove('msg.txt')
	os.remove('temp.file')
	os.remove('encrypted_key.bin')
	os.remove('signature.sha1')
	os.remove('repo.html')
	os.remove('to_publickey.pem')

# def format_message(msg_file):

def get_sender_email(msg_file):
	from_email = None
	with open(msg_file, 'r') as fp:
		for line in fp:
			if 'from' in line and 'to' in line:
				comma_index = line.index(',')
				from_email = line[6:comma_index]
				break
	print from_email
	return from_email

def get_sender_name_from_cert(cert_file):
	cmd = 'openssl x509 -in '+cert_file
	cmd += ' -email -noout'

	args = shlex.split(cmd)
	p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	p.wait()
	out, err = p.communicate()

	if p.returncode is not 0:
		print err
		raise Exception("Could not get email from certificate "+cert_file)
	return out

def receive_mail(msg_file):
	from_email = get_sender_email(msg_file)
	from_unity_id = from_email.split('@')[0]
	from_cert_name = get_certificate_for_key(from_unity_id)
	if not verify_certificate(from_cert_name):
		raise Exception("Certificate not valid: "+from_cert_name)
	email_from_cert = get_sender_name_from_cert(from_cert_name)
	print email_from_cert

	pub_key_file_name = get_public_key_from_cert(from_cert_name)
	cmd = 'openssl dgst -sha1 -verify '+pub_key_file_name
	cmd += ' -signature '
	public.key -signature file.sig file

init_structures()
print index

if args.send is not None:
	send_email(args.send[0])

if args.receive is not None:
	receive_mail(args.receive[0])