#!/usr/bin/env bash

# This script shows how to generate test keys and certs

# Generate valid CA for Management api
openssl genrsa -out dex-ca.key 4096
openssl req -new -x509 -days 365 -key dex-ca.key -out dex-ca.crt -subj "/CN=dex"

# Generate server key/cert
openssl genrsa -out dex.key 4096
openssl req -new -key dex.key -out dex.csr -subj "/CN=dex.test-karolina.nlpnp.adsdcsp.com"
openssl x509 -req -days 365 -in dex.csr -CA dex-ca.crt -CAkey dex-ca.key -set_serial 01 -out dex.crt
