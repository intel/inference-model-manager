#!/bin/bash
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

DOMAIN_NAME=$1
MINIO_ACCESS_KEY=$2
MINIO_SECRET_KEY=$3
MINIO_EXTERNAL_URL=$4
MINIO_REGION=$5
MINIO_SIGNATURE=$6
MGT_API_AUTHORIZATION=$7

export MGMT_DOMAIN_NAME=mgt.$DOMAIN_NAME
export MGT_NAMESPACE=mgt-api
export DOMAIN_NAME=$DOMAIN_NAME
export MINIO_EXTERNAL_URI=`echo "$MINIO_EXTERNAL_URL" | awk -F/ '{print $3}'`

. ../utils/fill_template.sh
. ../utils/messages.sh

cd $HELM_TEMP_DIR/management-api-subchart/certs

header "Generating certificates for IMM Management API"

# Copy previously generated ca-ing 
cp $HELM_TEMP_DIR/dex-subchart/certs/ca-ing.* ./ 

./generate-ing-management-api-certs.sh
./generate-management-api-certs.sh
./scriptcert.sh

kubectl get secret -n dex ca-secret-dex -o yaml | yq r - 'data."ca.crt"' | $B64DECODE > ca-dex.crt

cd -

cd $HELM_TEMP_DIR/management-api-subchart

header "Installation of Management API"

fill_template "<mgt_api_image>" $MGMT_IMAGE values.yaml
fill_template "<mgt_api_tag>" $MGMT_TAG values.yaml
fill_template "<management_api_desired_dns>" mgt.$DOMAIN_NAME values.yaml
fill_template "<dns_for_inference_endpoints>" $DOMAIN_NAME values.yaml
fill_template "<minio_access_key>" $MINIO_ACCESS_KEY values.yaml
fill_template "<minio_secret_key>" $MINIO_SECRET_KEY values.yaml
fill_template "<minio_endpoint>" $MINIO_EXTERNAL_URI values.yaml
fill_template "<minio_endpoint_url>" $MINIO_EXTERNAL_URL values.yaml
fill_template "<minio_signature>" $MINIO_SIGNATURE values.yaml
fill_template "<minio_region>" $MINIO_REGION values.yaml
fill_template "<groupName>" admin values.yaml
fill_template "<adminScope>" admin values.yaml
fill_template "<platformAdmin>" admin values.yaml
fill_template "<use_mgt_api_authorization>" $MGT_API_AUTHORIZATION values.yaml

helm install .
show_result $? "Installation of Management API succeded" "Failed to install Management API"

cd -
