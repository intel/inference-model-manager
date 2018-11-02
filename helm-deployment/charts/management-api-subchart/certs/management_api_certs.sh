#!/bin/bash

# This script shows how to generate test keys and certs

# Generate valid CA for Management api
openssl genrsa -out ca-man-api.key 4096
openssl req -new -x509 -days 365 -key ca-man-api.key -out ca-man-api.crt -subj "/CN=ca-man-api"

# Generate server key/cert
openssl genrsa -out man-api-server.key 4096
openssl req -new -key man-api-server.key -out man-api-server.csr -subj "/CN=management-api.aipg.com"
openssl x509 -req -days 365 -in man-api-server.csr -CA ca-man-api.crt -CAkey ca-man-api.key -set_serial 01 -out man-api-server.crt
