#!/bin/bash

# Generate invalid client certificate with improper subject name, but signed by proper CA (test purposes)
openssl genrsa -out bad-client.key 4096
openssl req -new -key bad-client.key -out bad-client.csr -subj "/CN=bad-client"
openssl x509 -req -days 365 -in bad-client.csr -CA ca-cert-tf.crt -CAkey ca-cert-tf.key -set_serial 01 -out bad-client.crt
