# Generate a CA to be used for creating client certificates
openssl genrsa -out ca-cert-tf.key 4096
openssl req -new -x509 -days 365 -key ca-cert-tf.key -out ca-cert-tf.crt -subj "/CN=ca"
# Generate client key and certificate authorizing access to inference endpoints. Change the CN as needed.
openssl genrsa -out client-tf.key 4096
openssl req -new -key client-tf.key -out client-tf.csr -subj "/CN=client"
openssl x509 -req -days 365 -in client-tf.csr -CA ca-cert-tf.crt -CAkey ca-cert-tf.key -set_serial 01 -out client-tf.crt
echo 01 > /tmp/certserial
echo 01 > /tmp/crlnumber
touch /tmp/certindex
openssl ca -config ca.conf -gencrl -keyfile ca-cert-tf.key -cert ca-cert-tf.crt -out root.crl.pem
cat root.crl.pem >> ca-cert-tf.crt
export CERT=`cat ca-cert-tf.crt|base64`

