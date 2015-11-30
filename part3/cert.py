import urllib2, os

def fetch_certificate(key): 
	cert_url = None
	with open('repo.html', 'r') as fp:
		for line in fp:
			chunks = line.split(',')
			if chunks[0] == key:
				cert_url = chunks[1]
				break
	return _save_certificate(key, cert_url)
	
def _save_certificate(key, url):
	print "Save cert called"
	response = urllib2.urlopen(url)
	html = response.read()
	path_to_db = os.getcwd()+'/db/'
	if not os.path.isdir(path_to_db):
		os.mkdir(path_to_db, 0755)

	name_of_cert = path_to_db+key
	with open(name_of_cert, 'w') as fp:
		fp.write(html)
	return name_of_cert

def fetch_ca_cert():
	response = urllib2.urlopen('https://courses.ncsu.edu/csc574/lec/001/wrap/Projects/root-ca.crt')
	html = response.read()
	with open('root-ca.crt', 'w') as fp:
		fp.write(html)

response = urllib2.urlopen('https://courses.ncsu.edu/csc574/lec/001/CertificateRepo')
html = response.read()
with open('repo.html', 'w') as fp:
	fp.write(html)
