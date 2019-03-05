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

CLUSTER_NAME=$1
DNS_DOMAIN_NAME=$2
export SED_CMD="gsed"
export ISSUER=https://dex.$DNS_DOMAIN_NAME:443/dex # change 443 port if using kubernetes node port instead of load balancer
export DEX_NAMESPACE=dex


./restart_k8sapi.sh $CLUSTER_NAME $ISSUER $DEX_NAMESPACE


