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
##
. ../utils/fill_template.sh
. ../utils/messages.sh

export ISSUER=$1
export DEX_NAMESPACE=$2
export DEX_DOMAIN_NAME=$3
header "Generating certificates for DEX"
cp dex-ing-ca.yaml $HELM_TEMP_DIR/dex-subchart/templates/
cd $HELM_TEMP_DIR/dex-subchart/certs
./generate-ing-ca.sh
./generate-dex-certs.sh 
./generate-ing-dex-certs.sh
cd -

header "Installing DEX"
cp ../../tests/deployment/dex_config.yaml ./
export OPENLDAP_SVC=`kubectl get svc|grep "openldap   "| awk '{ print $1 }'`
export OPENLDAP_SVC_ADDRESS="$OPENLDAP_SVC.default:389"
fill_template toreplacedbyissuer $ISSUER dex_config.yaml
fill_template toreplacedbyhost $OPENLDAP_SVC_ADDRESS dex_config.yaml
fill_template toreplacedbyldapaddress $OPENLDAP_SVC_ADDRESS dex_config.yaml
fill_template toreplacedbyissuer $ISSUER $HELM_TEMP_DIR/dex-subchart/values.yaml
fill_template toreplacedbyingresshosts $DEX_DOMAIN_NAME $HELM_TEMP_DIR/dex-subchart/values.yaml
fill_template toreplacedbyingresstlshosts $DEX_DOMAIN_NAME $HELM_TEMP_DIR/dex-subchart/values.yaml
helm install -f dex_config.yaml $HELM_TEMP_DIR/dex-subchart/
show_result $? "DEX installation succesful" "Failed to install DEX"
