#!/bin/bash
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
. ~/inference-model-manager/.venv/bin/activate
cd ~/inference-model-manager/scripts
. ./prepare_test_env.sh ${DOMAIN_NAME}
. ./imm_utils.sh
get_token admin
export ING_IP=`kubectl get services -n ingress-nginx|grep ingress-nginx|awk '{ print $(NF-2) }'`
cd ~/inference-model-manager/installer
./uninstaller.sh -q
sleep 3m
kops delete cluster ${CLUSTER_NAME} --yes
cd ~/inference-model-manager/installer/utils/route53
unset REQUESTS_CA_BUNDLE
unset MANAGEMENT_CA_CERT_PATH
unset CURL_CA_BUNDLE
./apply.sh DELETE ${ING_IP} ${DOMAIN_NAME}
deactivate
