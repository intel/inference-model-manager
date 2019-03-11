#!/usr/bin/env bash
#
# Copyright (c) 2018 Intel Corporation
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

RETURN_DIR=$PWD
if [ "$DEX_INTERNAL_CERTS" = "true" ]
then
echo "Internal dex certs will be generated"
cd ../../helm-deployment/dex-subchart/certs/ && ./generate-dex-certs.sh
cd $RETURN_DIR
fi

if [ "$DEX_CERTS" = "true" ]
then
echo "External dex self-signed certs will be generated for DNS ${DEX_DOMAIN_NAME}"
cd ../../helm-deployment/dex-subchart/certs/ && ./generate-ing-dex-certs.sh
cd $RETURN_DIR
fi
cp ../../helm-deployment/ldap-subchart/certs/ca.crt ldap.ca
helm install -f dex_config.yaml --set issuer=${ISSUER} --set ingress.hosts=${DEX_DOMAIN_NAME} --set ingress.tls.hosts=${DEX_DOMAIN_NAME} ../../helm-deployment/dex-subchart/
kubectl create secret generic root-ca --from-file=ldap.ca -n dex