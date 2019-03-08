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
export MGMT_DOMAIN_NAME="mgt.$DOMAIN_NAME"

echo "Fetching CA for $MGMT_DOMAIN_NAME"
./get_cert.sh $MGMT_DOMAIN_NAME ca-ing $PROXY > ca.pem
cat ./ca.pem
sudo cp ca.pem /usr/local/share/ca-certificates/imm-ca-ing.crt
sudo update-ca-certificates -f

if [[ "$OSTYPE" == "darwin"* ]]; then
    export CERT=`cat $HELM_TEMP_DIR/management-api-subchart/certs/ca-cert-tf.crt | base64`
else
    export CERT=`cat $HELM_TEMP_DIR/management-api-subchart/certs/ca-cert-tf.crt | base64 -w0`
fi
