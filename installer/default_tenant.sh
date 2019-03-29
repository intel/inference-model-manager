#
# Copyright (c) 2019 Intel Corporation
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
DEFAULT_TENANT_NAME=$DEFAULT_TENANT_NAME

. ./utils/messages.sh

. ../.venv/bin/activate

SCOPE='admin'
export USER_SCOPE=$SCOPE
export ADMIN_SCOPE=$SCOPE
export TENANT_RESOURCES={}

cd ../scripts
. ./imm_utils.sh

EXPECTED='{"status": "OK", "data": {"tenants": []}}'

while [[ "$TENANTS" != $EXPECTED ]]; do 
        get_token admin
        TENANTS=`./imm ls t`; 
        if [[ "$TENANTS" != $EXPECTED ]]; then
          echo "IMM not ready";         
          sleep 5; 
        fi
done

response=`yes | ./imm create t $DEFAULT_TENANT_NAME $SCOPE`
echo $response
[[ $response =~ "Tenant $DEFAULT_TENANT_NAME created" ]] && success "Successfully created default tenant $DEFAULT_TENANT_NAME" || failure "Failed to create default tenant $DEFAULT_TENANT_NAME"
cd -
