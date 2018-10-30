#!/bin/bash

# This script shows how to generate test keys and certs
# If you provide different value in annotations.allowed values than "CN=client", remember to change subject name also in client key

# Generate valid CA
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 365 -key ca.key -out ca.crt -subj "/CN=ca"

# Generate valid client key/cert
openssl genrsa -out client.key 4096
openssl req -new -key client.key -out client.csr -subj "/CN=client"
openssl x509 -req -days 365 -in client.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out client.crt

# Generate valid server key/cert
openssl genrsa -out server.key 4096
openssl req -new -key sesrver.key -out server.csr -subj "/CN=serving-service.kube.cluster"
openssl x509 -req -days 365 -in server.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out server.crt

# Generate valid CA for dex
openssl genrsa -out ca-cert-secret-dex.key 4096
openssl req -new -x509 -days 365 -key ca-cert-secret-dex.key -out ca-cert-secret-dex.crt -subj "/CN=ca-dex"

# Generate valid dex server key/cert
openssl genrsa -out dex.key 4096
openssl req -new -key dex.key -out dex.csr -subj "/CN=*.${DOMAIN_NAME}"
openssl x509 -req -days 365 -in dex.csr -CA ca-cert-secret-dex.crt -CAkey ca-cert-secret-dex.key -set_serial 01 -out server-dex.crt

