#!/bin/bash

# This script shows how to generate test keys and certs
# If you provide different value in annotations.allowed values than "CN=client", remember to change subject name also in client key

# Generate server key/cert
openssl genrsa -out server.key 4096
openssl req -new -x509 -days 365 -key server.key -out server.crt -subj "/CN=serving-service.kube.cluster"

# Generate valid CA
openssl genrsa -out ca-cert-secret.key 4096
openssl req -new -x509 -days 365 -key ca-cert-secret.key -out ca-cert-secret.crt -subj "/CN=ca"

# Generate valid client key/cert
openssl genrsa -out client.key 4096
openssl req -new -key client.key -out client.csr -subj "/CN=client"
openssl x509 -req -days 365 -in client.csr -CA ca-cert-secret.crt -CAkey ca-cert-secret.key -set_serial 01 -out client.crt
