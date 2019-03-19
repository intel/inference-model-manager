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

. ../utils/messages.sh
. ../utils/progress_bar.sh
DIR=`pwd`
cd $HELM_TEMP_DIR/ldap-subchart/
header "Installing LDAP"
cd certs
./genereate_ldap_certs.sh
cd ..
if [ "$MGT_API_AUTHORIZATION" == "true" ]; then
helm install --name imm-openldap -f ./customLdifFiles.yaml .
else
helm install --name imm-openldap -f ../../../tests/deployment/ldap/customLdifFiles.yaml .
fi
show_result $? "LDAP installation succeded" "Failed to install LDAP"
header "Waiting 4 minutes"
progress_bar 240
cd $DIR
