#!/usr/bin/env bash
RETURN_DIR=$PWD
if [ "$DEX_INTERNAL_CERTS" = "true" ]
then
echo "Internal dex certs will be generated"
cd ../../helm-deployment/dex-subchart/certs/ && ./internal_ing_dex_certs.sh
cd $RETURN_DIR
fi

if [ "$DEX_CERTS" = "true" ]
then
echo "External dex self-signed certs will be generated for DNS ${DEX_DOMAIN_NAME}"
cd ../../helm-deployment/dex-subchart/certs/ && ./generate-dex-certs.sh
cd $RETURN_DIR
fi
helm install -f dex_config.yaml --set issuer=${ISSUER} --set ingress.hosts=${DEX_DOMAIN_NAME} --set ingress.tls.hosts=${DEX_DOMAIN_NAME} ../../helm-deployment/dex-subchart/
