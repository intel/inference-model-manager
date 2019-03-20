#!/bin/bash
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

export DOMAIN_NAME=$1
export PROXY=$2
export DEX_DOMAIN_NAME="dex.$DOMAIN_NAME"
export MGMT_DOMAIN_NAME="mgt.$DOMAIN_NAME"

echo "Fetching CA for $MGMT_DOMAIN_NAME"
./get_cert_kubectl.sh > ca.pem
cat ./ca.pem

export REQUESTS_CA_BUNDLE=`pwd`/ca.pem
export MANAGEMENT_CA_CERT_PATH=`pwd`/ca.pem
export CURL_CA_BUNDLE=`pwd`/ca.pem


if [ "$MGT_API_AUTHORIZATION" == "true" ]; then
  USER_PASSWD=`kubectl get secret imm-openldap-customldif -o yaml|grep immconfig|awk '{ print $2 }'|base64 --decode|grep userpassword|awk '{ print $2 }'`
  USER_NAME=user@example.com
  export IMM_USER_CREDENTIALS=$USER_NAME:$USER_PASSWD
fi

export DEX_NAMESPACE="dex"
export MGT_NAMESPACE="mgt-api"
export DEX_URL=https://${DEX_DOMAIN_NAME}:443
export HELM_INSTALL_DIR="../installer/helm-temp-dir"
export CERT=`cat $HELM_INSTALL_DIR/management-api-subchart/certs/ca-cert-tf.crt | $B64ENCODE`
