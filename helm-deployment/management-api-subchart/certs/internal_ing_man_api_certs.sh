#!/usr/bin/env bash

# This script shows how to generate test keys and certs

# Generate CA
openssl genrsa -out ca-ing-man-api.key 4096
openssl req -new -x509 -days 365 -key ca-ing-man-api.key -out ca-ing-man-api.crt -subj "/CN=management-api.cluster"

# Generate server key/cert
openssl genrsa -out ing-man-api-server.key 4096
openssl req -new -key ing-man-api-server.key -out ing-man-api-server.csr -subj "/CN=management-api.cluster"
openssl x509 -req -days 365 -in ing-man-api-server.csr -CA ca-ing-man-api.crt -CAkey ca-ing-man-api.key -set_serial 01 -out ing-man-api-server.crt
