#!/usr/bin/env bats
#
# Copyright (c) 2018-2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


export TENANT_NAME="tenanttest"
export ENDPOINT_NAME="endpointtest"
export SERVING_NAME="tf-serving"
export MODEL_NAME="resnet"
export MODEL_VERSION=1
export MODEL_VERSION_POLICY="{latest {} }"
export ADMIN_SCOPE="test"
export USER_SCOPE="test"
export REPLICAS=2
export MODEL_PATH="saved_model.pb"
export NUMPY_PATH="10_v1_imgs.npy"
export IMAGE_LIST="images/airliner.jpeg,images/arctic-fox.jpeg,images/bee.jpeg,images/golden_retriever.jpeg,images/gorilla.jpeg,images/magnetic_compass.jpeg,images/peacock.jpeg,images/pelican.jpeg,images/snail.jpeg,images/zebra.jpeg"
export LABEL_LIST=" airliner, Arctic fox, bee, golden retriever, gorilla, magnetic compass, peacock, pelican, snail, zebra"
export JPEGS_INFERENCE_ACCURACY=0
export SERVER_CERT="server-tf.crt"
export CLIENT_CERT="client-tf.crt"
export CLIENT_KEY="client-tf.key"
export SAVED_MODEL_SRC="https://storage.googleapis.com/inference-eu/models_zoo/resnet_V1_50/saved_model/saved_model.pb"
export IMAGES_NUMPY_SRC="https://storage.googleapis.com/inference-eu/models_zoo/resnet_V1_50/datasets/10_v1_imgs.npy"

[[ ! -f ${MODEL_PATH} ]] && echo "Downloading model" && wget ${SAVED_MODEL_SRC}
[[ ! -f ${NUMPY_PATH} ]] && echo "Downloading numpy images" && wget ${IMAGES_NUMPY_SRC}

. ./imm_utils.sh

get_inference_accuracy(){
    NUMBER_OF_MATCHES=0
    IFS=',' read -ra LABELS <<< "$LABEL_LIST"
    for i in "${LABELS[@]}"; do
         [[ $* =~ "$i" ]] && let "NUMBER_OF_MATCHES++"
    done
    JPEGS_INFERENCE_ACCURACY=$((NUMBER_OF_MATCHES*10))
    echo "${JPEGS_INFERENCE_ACCURACY}"
}


[[ ! -f ${MODEL_PATH} ]] && echo "Downloading model" && wget https://storage.googleapis.com/inference-eu/models_zoo/resnet_V1_50/saved_model/saved_model.pb
[[ ! -f ${NUMPY_PATH} ]] && echo "Downloading numpy images" && wget https://storage.googleapis.com/inference-eu/models_zoo/resnet_V1_50/datasets/10_v1_imgs.npy

#"****************************ADMIN****************************"
@test "Get admin token" {
    response="$(get_token admin)"
    grep -E "Token is saved" <<< $response
}

@test "Create tenant" {
    response="$(yes | ./imm c t ${TENANT_NAME} ${ADMIN_SCOPE})"
    grep -E "${TENANT_NAME}" <<< $response
}

@test "List tenants" {
    response="$(./imm ls t)"
    grep -E "${TENANT_NAME}" <<< $response
}

@test "Logout" {
    response="$(yes | ./imm logout)"
    grep -E "Signed out" <<< $response
}

#"*****************************USER*****************************"
@test "Get user token" {
    response="$(get_token user)"
    grep -E "Token is saved" <<< $response
}

@test "Model upload" {
    response="$(./imm u ${MODEL_PATH} ${MODEL_NAME} ${MODEL_VERSION} ${TENANT_NAME})"
    echo "$response" >&3
    grep -E "completed successfully" <<< $response
}

@test "List models" {
    response="$(./imm ls m ${TENANT_NAME})"
    grep -E "${MODEL_NAME}" <<< $response
}

@test "Create endpoint" {
    response=`./imm c e ${ENDPOINT_NAME} ${MODEL_NAME} "${MODEL_VERSION_POLICY}" ${TENANT_NAME} ${SERVING_NAME}`
    echo "$response" >&3
    grep -E "${ENDPOINT_NAME}-${TENANT_NAME}.${DOMAIN_NAME}" <<< $response
}

@test "List endpoints" {
    response="$(./imm ls e ${TENANT_NAME})"
    grep -E "${ENDPOINT_NAME}" <<< $response
}

@test "Check if endpoint is up and running" {
    sleep 20
    run bash -c "./get_cert.sh ${ENDPOINT_NAME}-${TENANT_NAME}.${DOMAIN_NAME} ${DOMAIN_NAME} ${PROXY} > ${SERVER_CERT}"
    cat $SERVER_CERT
    while [[ ! $status =~ 'AVAILABLE' ]]; do sleep 5; status="$(./imm g ms ${ENDPOINT_NAME}-${TENANT_NAME}.${DOMAIN_NAME}:443 ${MODEL_NAME} ${SERVER_CERT} ${CLIENT_CERT} ${CLIENT_KEY})"; done
    # make sure that it started serving - it's better to wait little bit longer than suffer random failures in CI
    sleep 60
}

@test "Run inference on numpy file" {
    response="$(./imm ri ${ENDPOINT_NAME}-${TENANT_NAME}.${DOMAIN_NAME}:443 ${MODEL_NAME} numpy ${NUMPY_PATH} 10 ${SERVER_CERT} ${CLIENT_CERT} ${CLIENT_KEY})"
    echo "$response" >&3
    grep -E "Imagenet top results in a single batch" <<< $response
}

@test "Run inference on jpg images" {
    response="$(./imm ri ${ENDPOINT_NAME}-${TENANT_NAME}.${DOMAIN_NAME}:443 ${MODEL_NAME} list ${IMAGE_LIST} 1 ${SERVER_CERT} ${CLIENT_CERT} ${CLIENT_KEY})"
    echo "$response" >&3
    run get_inference_accuracy $response
    [ $output -ge 60 ]
}

@test "Scale endpoint" {
    response="$(./imm s e ${ENDPOINT_NAME} ${REPLICAS} ${TENANT_NAME})"
    grep -E "patched successfully. New values: {'replicas': ${REPLICAS}}" <<< $response
}

@test "List endpoints after scale" {
    response="$(./imm ls e ${TENANT_NAME})"
    grep -E "${ENDPOINT_NAME}" <<< $response
}

@test "Delete endpoint" {
    response="$(./imm rm e ${ENDPOINT_NAME} ${TENANT_NAME})"
    grep -E "${ENDPOINT_NAME}.*deleted" <<< $response
}

@test "List endpoints after removal" {
    response="$(./imm ls e ${TENANT_NAME})"
    grep -E "no endpoints present in ${TENANT_NAME} tenant" <<< $response
}

@test "Delete model" {
    response="$(./imm rm m ${MODEL_NAME} ${MODEL_VERSION} ${TENANT_NAME})"
    grep -E "Model deleted: ${MODEL_NAME}" <<< $response
}

@test "List models after removal" {
    response="$(./imm ls m ${TENANT_NAME})"
    grep -E "no models present in ${TENANT_NAME} tenant" <<< $response
}

@test "User logout" {
    response="$(yes | ./imm logout)"
    grep -E "Signed out" <<< $response
}

#"****************************ADMIN****************************"
@test "Get admin token after user logout" {
    response="$(get_token admin)"
    grep -E "Token is saved" <<< $response
}

@test "Delete tenant" {
    response="$(./imm rm t ${TENANT_NAME})"
    grep -E "${TENANT_NAME}" <<< $response
}

@test "List tenants after removal" {
    response="$(./imm ls t)"
    grep -E -v "${TENANT_NAME}" <<< $response
}

@test "Admin logout after tenant removal" {
    response="$(yes | ./imm logout)"
    grep -E "Signed out" <<< $response
}

