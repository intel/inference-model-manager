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
  TOKEN=""
  if [ ! -z "$SINGLE_TENANT_USER" ]; then    
    	TOKEN=`python ../tests/management_api_tests/authenticate.py $SINGLE_TENANT_USER`
  else
	    echo "Get $user token"
    	TOKEN=`python ../tests/management_api_tests/authenticate.py $user`
  fi
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
    resource=$2
    error_message=$1
    ./imm rm t $resource
    ./imm logout
    echo "Tests failed. Error occurred during ${error_message} test" 
    exit 1
}

# This function reads the variable name $1 where tenant name is/will be stored.
# If variable with name $1 is empty, it will read the input or store default value in that variable.
# It it's not empty, it will not change it's value 
get_tenant_name() {
        local __TENANT=$1
        local TENANT=${!__TENANT}
        if [[ -n ${DEFAULT_TENANT_NAME} ]]; then
             [[ -z ${TENANT} ]] && read -p "Please provide tenant name (default: $DEFAULT_TENANT_NAME) " TENANT
             [[ -z ${TENANT} ]] && TENANT=$DEFAULT_TENANT_NAME
        else
             [[ -z ${TENANT} ]] && read -p "Please provide tenant name " TENANT
        fi
        eval $__TENANT="'$TENANT'"
}
