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
DEFAULT_TENANT_NAME=$2
PROXY=$3

. ./utils/messages.sh

. ../.venv/bin/activate

SCOPE='admin'
export USER_SCOPE=$SCOPE ADMIN_SCOPE=$SCOPE
export TENANT_RESOURCES={}

cd ../scripts
. ./imm_utils.sh

get_token admin

response=`yes | ./imm create t $DEFAULT_TENANT_NAME $SCOPE`
show_result $? "Default tenant $DEFAULT_TENANT_NAME created" "Failed to create default tenant $DEFAULT_TENANT_NAME"

cd -
