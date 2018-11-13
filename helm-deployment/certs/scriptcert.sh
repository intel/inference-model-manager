#!/bin/bash

DOMAIN_NAME=$1

# This script shows how to generate test keys and certs
# If you provide different value in annotations.allowed values than "CN=client", remember to change subject name also in client key

# Generate valid CA for tf-serving
openssl genrsa -out ca-cert-tf.key 4096
openssl req -new -x509 -days 365 -key ca-cert-tf.key -out ca-cert-tf.crt -subj "/CN=ca"

# Generate valid client key/cert for tf serving
openssl genrsa -out client-tf.key 4096
openssl req -new -key client-tf.key -out client-tf.csr -subj "/CN=client"
openssl x509 -req -days 365 -in client-tf.csr -CA ca-cert-tf.crt -CAkey ca-cert-tf.key -set_serial 01 -out client-tf.crt

# Generate valid server key/cert for tf serving
openssl genrsa -out server-tf.key 4096
openssl req -new -x509 -days 365 -key server-tf.key -out server-tf.crt -subj "/CN=*.$DOMAIN_NAME"

# Generete empty CRL file
echo 01 > certserial
echo 01 > crlnumber
echo 01 > crlnumber
touch certindex
openssl ca -config ca.conf -gencrl -keyfile ca-cert-tf.key -cert ca-cert-tf.crt -out root.crl.pem
cat root.crl.pem >> ca-cert-tf.crt

