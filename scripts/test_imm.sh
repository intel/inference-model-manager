#!/bin/bash

TENANT_NAME="tenanttest"
ENDPOINT_NAME="endpointtest"
SERVING_NAME="tf-serving"
MODEL_NAME="resnet"
MODEL_VERSION=1
MODEL_VERSION_POLICY="{latest {} }"
ADMIN_SCOPE="test"
USER_SCOPE="test"
REPLICAS=2
MODEL_PATH="saved_model.pb"
NUMPY_PATH="10_v1_imgs.npy"
IMAGE_LIST="images/airliner.jpeg,images/arctic-fox.jpeg,images/bee.jpeg,images/golden_retriever.jpeg,images/gorilla.jpeg,images/magnetic_compass.jpeg,images/peacock.jpeg,images/pelican.jpeg,images/snail.jpeg,images/zebra.jpeg"
LABEL_LIST=" airliner, Arctic fox, bee, golden retriever, gorilla, magnetic compass, peacock, pelican, snail, zebra"
TESTS_NUMBER=0
PASSED_TESTS=0
JPEGS_INFERENCE_ACCURACY=0

SERVER_CERT="../helm-deployment/management-api-subchart/certs/server-tf.crt"
CLIENT_CERT="../helm-deployment/management-api-subchart/certs/client-tf.crt"
CLIENT_KEY="../helm-deployment/management-api-subchart/certs/client-tf.key"

SAVED_MODEL_SRC="https://storage.googleapis.com/inference-eu/models_zoo/resnet_V1_50/saved_model/saved_model.pb"
IMAGES_NUMPY_SRC="https://storage.googleapis.com/inference-eu/models_zoo/resnet_V1_50/datasets/10_v1_imgs.npy"

[[ ! -f ${MODEL_PATH} ]] && echo "Downloading model" && wget ${SAVED_MODEL_SRC}
[[ ! -f ${NUMPY_PATH} ]] && echo "Downloading numpy images" && wget ${IMAGES_NUMPY_SRC}

. ./imm_utils.sh

get_inference_accuracy(){
    NUMBER_OF_MATCHES=0
    IFS=',' read -ra LABELS <<< "$LABEL_LIST"
    for i in "${LABELS[@]}"; do
         [[ $* =~ "$i" ]] && let "NUMBER_OF_MATCHES++"
    done
    echo "Number of correct predictions: ${NUMBER_OF_MATCHES}"
    JPEGS_INFERENCE_ACCURACY=$((NUMBER_OF_MATCHES*10))
    echo "JPEGS inference accuracy: ${JPEGS_INFERENCE_ACCURACY}%"
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
[[ $response =~ "completed successfully" ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || { echo "Test failed: $response" && remove_resources "model upload" ${TENANT_NAME}; }

echo "List models"
response=`./imm ls m ${TENANT_NAME}`
let "TESTS_NUMBER++"
[[ $response =~ ${MODEL_NAME} ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || echo "Test failed: $response"

echo "Create endpoint"
response=`./imm c e ${ENDPOINT_NAME} ${MODEL_NAME} "${MODEL_VERSION_POLICY}" ${TENANT_NAME} ${SERVING_NAME}`
let "TESTS_NUMBER++"
[[ $response =~ "${ENDPOINT_NAME}-${TENANT_NAME}.${DOMAIN_NAME}" ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || { echo "Test failed: $response" && remove_resources "create endpoint" ${TENANT_NAME}; }

echo "List endpoints"
response=`./imm ls e ${TENANT_NAME}`
let "TESTS_NUMBER++"
[[ $response =~ "${ENDPOINT_NAME}" ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || echo "Test failed: $response"

echo "Waiting for running inference endpoint"
while [[ ! $status =~ 'AVAILABLE' ]]; do sleep 5; status=`python ../examples/grpc_client/grpc_client.py "${ENDPOINT_NAME}-${TENANT_NAME}.${DOMAIN_NAME}:443" ${MODEL_NAME} --get_model_status --server_cert ${SERVER_CERT} --client_cert ${CLIENT_CERT} --client_key ${CLIENT_KEY}`; echo -n "*"; done
echo -e "\n"

echo "Run inference on numpy file"
response=`./imm ri "${ENDPOINT_NAME}-${TENANT_NAME}.${DOMAIN_NAME}:443" ${MODEL_NAME} numpy ${NUMPY_PATH} 10 ${SERVER_CERT} ${CLIENT_CERT} ${CLIENT_KEY}`
let "TESTS_NUMBER++"
[[ $response =~ "Imagenet top results in a single batch" ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || echo "Test failed: $response"

echo "Run inference on jpg images"
response=`./imm ri "${ENDPOINT_NAME}-${TENANT_NAME}.${DOMAIN_NAME}:443" ${MODEL_NAME} list ${IMAGE_LIST} 1 ${SERVER_CERT} ${CLIENT_CERT} ${CLIENT_KEY}`
let "TESTS_NUMBER++"
get_inference_accuracy $response
[[ $JPEGS_INFERENCE_ACCURACY -ge 60  ]] && { echo "Test passed" && let "PASSED_TESTS++"; } || echo "Test failed: $response"

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

