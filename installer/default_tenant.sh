#!/usr/bin/env bash

DEFAULT_TENANT_NAME=$1
. ./utils/messages.sh

. ../.venv/bin/activate

CLIENT=`openssl x509 -noout -subject -in ../helm-deployment/management-api-subchart/certs/client-tf.crt | sed -n '/^subject/s/^.*CN=//p'`

cd ../scripts
. ./imm_utils.sh

get_token admin

header "Creating default tenant"
no | ./imm create t $DEFAULT_TENANT_NAME $CLIENT
