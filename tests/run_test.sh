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

export MANAGEMENT_API_URL="https://${MGMT_DOMAIN_NAME}:443"
echo "URL FOR MANAGEMENT API: $MANAGEMENT_API_URL"

export DEX_URL="https://${DEX_DOMAIN_NAME}:443"
echo "URL FOR DEX: $DEX_URL"

MINIO_SECRET_KEY=`kubectl get secret minio-access-info -n mgt-api -o 'go-template={{index .data "minio.access_secret_key"}}' | base64 -d`
echo $MINIO_SECRET_KEY

MINIO_ACCESS_KEY=`kubectl get secret minio-access-info -n mgt-api -o 'go-template={{index .data "minio.access_key_id"}}' | base64 -d`
echo $MINIO_ACCESS_KEY

export MINIO_ENDPOINT_ADDR='http://127.0.0.1:9000'
export MINIO_POD=`kubectl get pod | grep minio | awk '{print $1}'`
kubectl port-forward ${MINIO_POD} 9000:9000 &

pytest -v

echo "Stop port forwarding"
pkill -e -f "port-forward"
echo "Pkill succeded"


exit 0
