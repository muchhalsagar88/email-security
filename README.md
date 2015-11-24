Generate key pair and CSR
openssl genrsa -out key.pem 1024 # generate the key pair
openssl rsa -in key.pem -text -noout > out.txt # output in text format
openssl req -new -sha256 -key key.pem -out custom.csr # create a CSR
openssl req -noout -text -in custom.csr > opt_csr.txt  # output CSR in text format
openssl rsa -in key.pem -des3 -out enc-key.pem # password protect pem file (password: sagar)
