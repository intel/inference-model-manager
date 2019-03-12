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

IMM_CONFIG_PATH=~/.immconfig

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
	DEFAULT_TENANT=""
	if [ ! -z "$DEFAULT_TENANT_NAME" ]; then
	    DEFAULT_TENANT=", \"default_tenant\": \"${DEFAULT_TENANT_NAME}\""
	fi
	IMM_CFG="{\"management_api_port\": 443, \"management_api_address\": \"${MGMT_DOMAIN_NAME}\", \"ca_cert_path\": \"null\", \"access_token\": \"${ACCESS_TOKEN}\", \"id_token\": \"${ID_TOKEN}\", \"token_type\": \"${TOKEN_TYPE}\", \"refresh_token\": \"${REFRESH_TOKEN}\", \"expires_in\": \"${EXPIRES_IN}\", \"expires_at\": \"${EXPIRES_AT}\" $DEFAULT_TENANT}"
	echo ${IMM_CFG} > ${IMM_CONFIG_PATH}
	echo "Token is saved in ${IMM_CONFIG_PATH}"
}

remove_resources() {
    resource=$2
    error_message=$1
    ./imm rm t $resource
    ./imm logout
    echo "Tests failed. Error occurred during ${error_message} test" 
    exit 1
}
