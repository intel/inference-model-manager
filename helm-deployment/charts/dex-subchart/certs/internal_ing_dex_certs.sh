#!/usr/bin/env bash

# This script shows how to generate test keys and certs

# Generate CA
openssl genrsa -out ca-ing-dex.key 4096
openssl req -new -x509 -days 365 -key ca-ing-dex.key -out ca-ing-dex.crt -subj "/CN=dex.cluster"

# Generate server key/cert
openssl genrsa -out ing-dex.key 4096
openssl req -new -key ing-dex.key -out ing-dex.csr -subj "/CN=dex"
openssl x509 -req -days 365 -in ing-dex.csr -CA ca-ing-dex.crt -CAkey ca-ing-dex.key -set_serial 01 -out ing-dex.crt
