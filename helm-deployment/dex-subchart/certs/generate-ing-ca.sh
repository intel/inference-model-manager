# Generate valid CA for ingress
openssl genrsa -out ca-ing.key 4096
openssl req -new -x509 -days 365 -key ca-ing.key -out ca-ing.crt -subj "/CN=ca-ing"

