#!/usr/bin/env bash

TENANT_NAME="tenanttest"
ENDPOINT_NAME="endpointtest"
SERVING_NAME="tf-serving"
MODEL_NAME="resnet"
MODEL_VERSION=1
MODEL_VERSION_POLICY="{latest{}}"
ADMIN_SCOPE="test"
USER_SCOPE="test"
REPLICAS=2
IMM_CONFIG_PATH=~/.imm
MODEL_PATH="saved_model.pb"
NUMPY_PATH="10_v1_imgs.npy"
TESTS_NUMBER=0
PASSED_TESTS=0

SERVER_CERT="../helm-deployment/management-api-subchart/certs/server-tf.crt"
CLIENT_CERT="../helm-deployment/management-api-subchart/certs/client-tf.crt"
CLIENT_KEY="../helm-deployment/management-api-subchart/certs/client-tf.key"

get_token() {
	user=$1
	echo "Get $user token"
	TOKEN=`python -W ignore ../tests/management_api_tests/authenticate.py $user`
	TOKEN=`echo $TOKEN | tr \' \"`
	ACCESS_TOKEN=`echo $TOKEN | jq -r '.access_token'`
	TOKEN_TYPE=`echo $TOKEN | jq -r '.token_type'`
	EXPIRES_IN=`echo $TOKEN | jq -r '.expires_in'`
	REFRESH_TOKEN=`echo $TOKEN | jq -r '.refresh_token'`
	ID_TOKEN=`echo $TOKEN | jq -r '.id_token'`
	EXPIRES_AT=`echo $TOKEN | jq -r '.expires_at'`
	IMM_CFG="{\"management_api_port\": 443, \"management_api_address\": \"${MGMT_DOMAIN_NAME}\", \"ca_cert_path\": \"null\", \"access_token\": \"${ACCESS_TOKEN}\", \"id_token\": \"${ID_TOKEN}\", \"token_type\": \"${TOKEN_TYPE}\", \"refresh_token\": \"${REFRESH_TOKEN}\", \"expires_in\": \"${EXPIRES_IN}\", \"expires_at\": \"${EXPIRES_AT}\"}"
	echo ${IMM_CFG} > ${IMM_CONFIG_PATH}
	echo "Token is saved in ${IMM_CONFIG_PATH}"
}

remove_resources() {
    error_message=$1
    ./imm rm t ${TENANT_NAME}
    ./imm logout
    echo "Tests failed. Error occurred during ${error_message} test" 
    exit 1
}

[[ ! -f ${MODEL_PATH} ]] && echo "Downloading model" && wget https://storage.googleapis.com/inference-eu/models_zoo/resnet_V1_50/saved_model/saved_model.pb 
[[ ! -f ${NUMPY_PATH} ]] && echo "Downloading numpy images" && wget https://storage.googleapis.com/inference-eu/models_zoo/resnet_V1_50/datasets/10_v1_imgs.npy

echo "****************************ADMIN****************************"
get_token admin

echo "Create tenant"
response=`yes n | ./imm c t ${TENANT_NAME} ${ADMIN_SCOPE}`
let "TESTS_NUMBER++"
[[ $response =~ "${TENANT_NAME} created" ]] && { echo "Test passed" && let "++PASSED_TESTS"; } || { echo "Test failed: $response" && exit 1; }

echo "List tenants"
response=`./imm ls t`
let "TESTS_NUMBER++"
[[ $response =~ "${TENANT_NAME}" ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || echo "Test failed: $response" 

echo "Logout"
response=`yes | ./imm logout`
let "TESTS_NUMBER++"
[[ $response =~ "Signed out" ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || echo "Test failed: $response"

echo "*****************************USER*****************************"
get_token user

echo "Model upload"
response=`./imm u ${MODEL_PATH} ${MODEL_NAME} ${MODEL_VERSION} ${TENANT_NAME}`
let "TESTS_NUMBER++"
[[ $response =~ "completed successfully" ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || { echo "Test failed: $response" && remove_resources "model upload"; }

echo "List models"
response=`./imm ls m ${TENANT_NAME}`
let "TESTS_NUMBER++"
[[ $response =~ ${MODEL_NAME} ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || echo "Test failed: $response"

echo "Create endpoint"
response=`./imm c e ${ENDPOINT_NAME} ${MODEL_NAME} ${MODEL_VERSION_POLICY} ${TENANT_NAME} ${SERVING_NAME}`
let "TESTS_NUMBER++"
[[ $response =~ "${ENDPOINT_NAME}-${TENANT_NAME}.${DOMAIN_NAME}" ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || { echo "Test failed: $response" && remove_resources "create endpoint"; }

echo "List endpoints"
response=`./imm ls e ${TENANT_NAME}`
let "TESTS_NUMBER++"
[[ $response =~ "${ENDPOINT_NAME}" ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || echo "Test failed: $response"

echo "Waiting for running inference endpoint"
for i in {1..60}
do
	echo -n "*"
	sleep 1s
done
echo -e "\n"

echo "Run inference"
response=`./imm ri "${ENDPOINT_NAME}-${TENANT_NAME}.${DOMAIN_NAME}:443" ${MODEL_NAME} numpy ${NUMPY_PATH} 10 ${SERVER_CERT} ${CLIENT_CERT} ${CLIENT_KEY}`
let "TESTS_NUMBER++"
[[ $response =~ "Imagenet top results in a single batch" ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || echo "Test failed: $response"

echo "Scale endpoint"
response=`./imm s e ${ENDPOINT_NAME} ${REPLICAS} ${TENANT_NAME}`
let "TESTS_NUMBER++"
[[ $response =~ "patched successfully. New values: {'replicas': ${REPLICAS}}" ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || echo "Test failed: $response"

echo "List endpoints"
response=`./imm ls e ${TENANT_NAME}`
let "TESTS_NUMBER++"
[[ $response =~ "${ENDPOINT_NAME}" ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || echo "Test failed: $response"

echo "Delete endpoint"
response=`./imm rm e ${ENDPOINT_NAME} ${TENANT_NAME}`
let "TESTS_NUMBER++"
[[ $response =~ ${ENDPOINT_NAME}.*deleted ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || echo "Test failed: $response"

echo "List endpoints"
response=`./imm ls e ${TENANT_NAME}`
let "TESTS_NUMBER++"
[[ $response =~ "no endpoints present in ${TENANT_NAME} tenant" ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || echo "Test failed: $response"

echo "Delete model"
response=`./imm rm m ${MODEL_NAME} ${MODEL_VERSION} ${TENANT_NAME}`
let "TESTS_NUMBER++"
[[ $response =~ "Model deleted: ${MODEL_NAME}" ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || echo "Test failed: $response"

echo "List models"
response=`./imm ls m ${TENANT_NAME}`
let "TESTS_NUMBER++"
[[ $response =~ "no models present in ${TENANT_NAME} tenant" ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || echo "Test failed: $response"

echo "Logout"
response=`yes | ./imm logout`
let "TESTS_NUMBER++"
[[ $response =~ "Signed out" ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || echo "Test failed: $response"

echo "****************************ADMIN****************************"
get_token admin

echo "Delete tenant"
response=`./imm rm t ${TENANT_NAME}`
let "TESTS_NUMBER++"
[[ $response =~ "${TENANT_NAME} deleted" ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || echo "Test failed: $response"

echo "List tenants"
response=`./imm ls t`
let "TESTS_NUMBER++"
[[ ! $response =~ "${TENANT_NAME}" ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || echo "Test failed: $response"

echo "Logout"
response=`yes | ./imm logout`
let "TESTS_NUMBER++"
[[ $response =~ "Signed out" ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || echo "Test failed: $response"

echo "Tests: ${TESTS_NUMBER}"
echo "Passed: ${PASSED_TESTS}"
[[ ${TESTS_NUMBER} -ne ${PASSED_TESTS} ]] && { echo "Tests failed" && exit 1; } || { echo "All tests passed" && exit 0; }

