#!/usr/bin/env bash
RETURN_DIR=$PWD
if [ "$MGMT_INTERNAL_CERTS" = "true" ]
then
echo "Internal mgmt-api certs will be generated"
cd ../../helm-deployment/management-api-subchart/certs/ && ./internal_ing_man_api_certs.sh
cd $RETURN_DIR
fi
if [ "$MGMT_CERTS" = "true" ]
then
echo "External mgmt-api self-signed certs will be generated for DNS ${MGMT_DOMAIN_NAME}"
cd ../../helm-deployment/management-api-subchart/certs/ && ./management_api_certs.sh
cd $RETURN_DIR
fi
MINIO_URL="http://minioplatform:9000"
helm install --set image=$MGMT_IMAGE --set tag=$MGMT_TAG --set platformDomain=$DOMAIN_NAME --set ingress.hosts=${MGMT_DOMAIN_NAME} --set ingress.tls.hosts=${MGMT_DOMAIN_NAME} ../../helm-deployment/management-api-subchart/
