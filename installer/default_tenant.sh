#!/usr/bin/env bash

. ../.venv/bin/activate

CLIENT=`openssl x509 -noout -subject -in ../helm-deployment/management-api-subchart/certs/client-tf.crt | sed -n '/^subject/s/^.*CN=//p'`

cd ../scripts
. ./imm_utils.sh

get_token admin
./imm create t default-tenant $CLIENT n
