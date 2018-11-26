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
echo "deploy imm ldap"
source ./deployment_imm_ldap.sh
OPENLDAP_SVC=`kubectl get svc|grep "openldap   "| awk '{ print $1 }'`
OPENLDAP_SVC_ADDRESS="$OPENLDAP_SVC:389"
echo $OPENLDAP_SVC_ADDRESS
sed -i "s@toreplacebyldapaddress@${OPENLDAP_SVC_ADDRESS}@g" dex_config.yaml
echo "deploy ingress"
source ./deployment_ingress.sh
echo "deploy CRD"
source ./deployment_crd.sh
echo "deploy minio"
source ./deployment_minio.sh
echo "deploy dex"
source ./deployment_dex.sh
echo "deploy management api"
source ./deployment_management_api.sh
