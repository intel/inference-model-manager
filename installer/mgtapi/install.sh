DOMAIN_NAME=$1
MINIO_ACCESS_KEY=$2
MINIO_SECRET_KEY=$3
MINIO_ENDPOINT=$4

export MGMT_DOMAIN_NAME=mgt.$DOMAIN_NAME
export MGT_NAMESPACE=mgt-api
export DOMAIN_NAME=$DOMAIN_NAME

. ../utils/fill_template.sh
. ../utils/messages.sh

cd ../../helm-deployment/management-api-subchart/certs

header "Generating certificates for IMM Management API"

./generate-ing-management-api-certs.sh
./generate-management-api-certs.sh
./scriptcert.sh


kubectl get secret ca-secret-dex -n dex -o yaml > dex_ca.yaml && yq r dex_ca.yaml data|awk '{ print $2 }'|base64 --decode > ca-dex.crt

cd -

cd ../../helm-deployment/management-api-subchart

header "Installation of Management API"

fill_template "<management_api_desired_dns>" mgt.$DOMAIN_NAME values.yaml
fill_template "<dns_for_inference_endpoints>" $DOMAIN_NAME values.yaml
fill_template "<minio_access_key>" $MINIO_ACCESS_KEY values.yaml
fill_template "<minio_secret_key>" $MINIO_SECRET_KEY values.yaml
fill_template "<minio_endpoint>" $MINIO_ENDPOINT values.yaml
fill_template "<minio_endpoint_url>" http://$MINIO_ENDPOINT values.yaml
fill_template "<groupName>" admin values.yaml
fill_template "<adminScope>" admin values.yaml
fill_template "<platformAdmin>" admin values.yaml

helm install .
show_result $? "Installation of Management API succeded" "Failed to install Management API"

cd -
