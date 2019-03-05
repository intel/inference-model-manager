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
#!/bin/bash
. ../utils/fill_template.sh
. ../utils/messages.sh

export ISSUER=$1
export DEX_NAMESPACE=$2
export DEX_DOMAIN_NAME=$3
header "Generating certificates for DEX"
cd $HELM_TEMP_DIR/dex-subchart/certs
./generate-ing-ca.sh
./generate-dex-certs.sh 
./generate-ing-dex-certs.sh
cd -

header "Installing DEX"
cp dex_config_tmpl.yaml dex_config.yaml
fill_template "toreplacedbyissuer" $ISSUER dex_config.yaml
export OPENLDAP_SVC=`kubectl get svc|grep "openldap   "| awk '{ print $1 }'`
export OPENLDAP_SVC_ADDRESS="$OPENLDAP_SVC.default:389"
fill_template "toreplacebyldapaddress" $OPENLDAP_SVC_ADDRESS dex_config.yaml
helm install -f dex_config.yaml --set issuer=${ISSUER} --set ingress.hosts=${DEX_DOMAIN_NAME} --set ingress.tls.hosts=${DEX_DOMAIN_NAME} $HELM_TEMP_DIR/dex-subchart/
show_result $? "DEX installation succesful" "Failed to install DEX"
