#!/bin/bash
export DOMAIN_NAME=$1
export PROXY=$2
export DEX_DOMAIN_NAME="dex.$DOMAIN_NAME"
export MGMT_DOMAIN_NAME="mgt.$DOMAIN_NAME"
echo "Fetching CA for $MGMT_DOMAIN_NAME"
./get_ca_cert.sh $MGMT_DOMAIN_NAME $PROXY> ca.pem
cat ./ca.pem
export REQUESTS_CA_BUNDLE=`pwd`/ca.pem
export CURL_CA_BUNDLE=`pwd`/ca.pem

export DEX_NAMESPACE="dex"
export MGT_NAMESPACE="mgt-api"
export DEX_URL=https://${DEX_DOMAIN_NAME}:443
export HELM_INSTALL_DIR="../installer/helm-temp-dir"
export CERT=`cat $HELM_INSTALL_DIR/management-api-subchart/certs/ca-cert-tf.crt | base64 -w0`
