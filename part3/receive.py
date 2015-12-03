import  sys, os, string, shlex, subprocess
from cert import fetch_certificate

def read_lines_from_file(input_file, from_line, to_line):
	count = 1
	content = ''
	with open(input_file, 'rb') as fp:
		for line in fp:
			if count >= from_line and count <= to_line:
				content += line
			elif count>to_line:
				break
			count += 1
	return content

def get_sender_email(msg_file):
	line  = read_lines_from_file(msg_file, 1, 1)
	comma_index = line.index(',')
	from_email = line[6:comma_index]
	return from_email

def get_session_key(input_file):
	count = 1
	content = ''
	with open(input_file, 'rb') as fp:
		for line in fp:
			if count >= 3:
				if line != '\n':
					content += line
				else:
					break
			count += 1
	with open('encrypted_session_key.bin', 'wb') as fp:
		fp.write(content[:-1])

def get_msg_to_verify(input_file):
	count = 1
	content = ''
	new_line_count = 0
	with open(input_file, 'rb') as fp:
		for line in fp:
			if count >= 3:
				if new_line_count!=2:
					if line == '\n':
						new_line_count += 1
					if new_line_count != 2:
						content += line
				else:
					break
			count += 1
	with open('message_verify.bin', 'wb') as fp:
		fp.write(content)

def get_actual_msg_to_decrypt(input_file):
	start_recording = False
	count = 0
	content = ''
	with open(input_file, 'rb') as fp:
		for line in fp:
			if line != '\n' and start_recording:
				content += line
			elif line == '\n':
				count += 1
				if count < 2:
					start_recording = True
				else:
					start_recording = False
					break
	with open('actual_enc_message.bin', 'wb') as fp:
		fp.write(content)

def get_sign_for_verification(input_file):
	content = ''
	new_line_count = 0
	with open(input_file, 'rb') as fp:
		for line in fp:
			if new_line_count<2:
				if line == '\n':
					new_line_count += 1
			else:
				if 'END CSC574' not in line:
					content += line
	with open('sign_verify.bin', 'wb') as fp:
		fp.write(content)

def clean_decryption():
	os.remove('encrypted_session_key.bin')
	os.remove('message_verify.bin')
	os.remove('sign_verify.bin')
	os.remove('actual_enc_message.bin')

def format_incoming_message(message_file):
	get_session_key(message_file)
	get_msg_to_verify(message_file)
	get_sign_for_verification(message_file)
	get_actual_msg_to_decrypt(message_file)
