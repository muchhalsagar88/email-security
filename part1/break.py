import subprocess, shlex, os 
from concurrent import futures

class Key_Generator():
	
	def __init__(self, len=3, start='a', end='z'):
		self.len = len
		self.start = start
		self.end = end
		self.position_values = [0]*len
		self.end_flag = False

	def get_next_key(self):
		if not self.end_flag:
			key = self.get_string()
			self.increment_positions()
			return key
		else:
			return None

	def get_string(self):
		a = []
		for x in self.position_values:
			a.append(self._get_alphabet(x))
		return ''.join(a)

	def increment_positions(self):
		for i in range(len(self.position_values)-1, -1, -1):
			curr = self.position_values[i]
			curr += 1
			if curr == ord(self.end)-ord(self.start)+1:
				if i == 0:
					self.end_flag = True
				else:
					self.position_values[i] = 0
			else:
				self.position_values[i] = curr
				break

	def _get_alphabet(self, value):
		return chr(97+value)

def decrypt_with_key(key):
	decrypt_file_name = 'input_'+key+'.txt'
	cmd = 'openssl enc -des-cbc -d -base64 -in outfile.txt -out '
	cmd += decrypt_file_name 
	cmd += ' -k '+key
	
	args = shlex.split(cmd)
	p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	p.wait()
	out, err = p.communicate()
		
	if p.returncode is not 0:
		os.remove(os.getcwd()+'/'+decrypt_file_name)
		# print "Error"
	else:
		print "Done with key: "+key

keygen = Key_Generator()
keys = []
key = keygen.get_next_key()
while (key is not None):
	keys.append(key)
	key = keygen.get_next_key()

with futures.ThreadPoolExecutor(max_workers=5) as executor:
    # Start the load operations and mark each future with its URL
    future_to_url = {executor.submit(decrypt_with_key, key): key for key in keys}
    # for future in futures.as_completed(future_to_url):
    #     url = future_to_url[future]
    #     try:
    #         data = future.result()
    #     except Exception as exc:
    #         print('%r generated an exception: %s' % (url, exc))
    #     else:
    #         print('%r page is %d bytes' % (url, len(data)))

