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
#!/bin/bash

DOMAIN_NAME=$1
PROXY=$2
DEFAULT_TENANT_NAME=$3

. ./utils/messages.sh
. ./prepare_test_env.sh $DOMAIN_NAME $PROXY

. ../.venv/bin/activate

CLIENT=`openssl x509 -noout -subject -in $HELM_TEMP_DIR/management-api-subchart/certs/client-tf.crt | sed -n '/^subject/s/^.*CN=//p'`
export TENANT_RESOURCES={}

cd ../scripts
. ./imm_utils.sh

get_token admin

header "Creating default tenant"
response=`yes n | ./imm create t $DEFAULT_TENANT_NAME $CLIENT`
echo $response

cd ../installer
