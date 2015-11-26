import sys, os, argparse
import atexit
from os.path import basename

# Global variables for index file and certificate file names
INDEX_FILE = os.getcwd()+'/index.db'
CERT_DB = os.getcwd()+'/cert.db'

# In-memory index
index = {}

parser = argparse.ArgumentParser(prog='email_utils', usage='%(prog)s [options]')
parser.add_argument('--add', nargs=1, type=str, 
	help='Adds a folder containing certificates or a single certificate to the database')
args = parser.parse_args()

def add_certificates(path):
	if os.path.exists(path) and not os.path.isfile(path):
		dirs = os.listdir(path)
		for cert in dirs:
			_add_certificate(path+cert)
	elif os.path.exists(path) and os.path.isfile(path):
		_add_certificate(path)
	else:
		print "Please provide a valid path"
		sys.exit(-1)

def _add_certificate(path):
	print "path: "+path
	with open(path, 'r') as fp:
		content = fp.read()
		file_name = basename(path)
		size = len(content)
		offset = write_to_db(content)
		add_key_to_index(file_name, offset, size)

def add_key_to_index(key, offset, length):
	index[key] = {
		'offset': offset,
		'length': length
	}

def init_structures():
	_populate_index()

def _populate_index():
	if os.path.exists(INDEX_FILE) and os.path.isfile(INDEX_FILE):
		with open(INDEX_FILE, 'r') as fp:
			for line in fp:
				chunks = line.split()
				index[chunks[0]] = {
					'offset': int(chunks[1]),
					'length': int(chunks[2])
				}
			print "Populated email indexing"

def persist_index():
	line = ''
	with open(INDEX_FILE, 'w') as fp:
		for pair in index.items():
			line += str(pair[0]) +' '+ str(pair[1]['offset']) +' '+str(pair[1]['length'])+'\n'
		line = line[:-1]
		fp.seek(0, 0)
		fp.write(line)

def read_db(offset, length):
	if os.path.exists(CERT_DB) and os.path.isfile(CERT_DB):
		with open(CERT_DB, 'r') as fp:
			fp.seek(offset, 0)
			return fp.read(length)

# returns start offset of data in file
def write_to_db(data):
	offset = 0
	if os.path.exists(CERT_DB) and os.path.isfile(CERT_DB):
		with open(CERT_DB, 'a+') as fp:
			# Move to the last byte
			fp.seek(0, 2)
			offset = fp.tell()
			fp.write(data)
	else:
		with open(CERT_DB, 'w+') as fp:
			fp.write(data)
	return offset

if args.add is not None:
	add_certificates(args.add[0])

atexit.register(persist_index)
init_structures()
print index

#print read_db(0, 12)