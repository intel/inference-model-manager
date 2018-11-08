#!/usr/bin/env bash
# Script to generate valid certs for dex

# Generate valid CA for dex
openssl genrsa -out dex-ca.key 4096
openssl req -new -x509 -days 365 -key dex-ca.key -out dex-ca.crt -subj "/CN=ca-dex"

# Generate valid dex server key/cert
openssl genrsa -out dex.key 4096
openssl req -new -key dex.key -out dex.csr -subj "/CN=${DOMAIN_NAME}"
openssl x509 -req -days 365 -in dex.csr -CA dex-ca.crt -CAkey dex-ca.key -set_serial 01 -out dex.crt
