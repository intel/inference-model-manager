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

. ../utils/fill_template.sh
. ../utils/messages.sh
MINIO_ACCESS_KEY=$1
MINIO_SECRET_KEY=$2
MINIO_EXTERNAL_URI=`echo "$3" | awk -F/ '{print $3}'`
RELEASE_NAME="$4-minio"

header "Installing test minio storage"

cd $HELM_TEMP_DIR/minio-subchart
fill_template "<minio_access_key>" $MINIO_ACCESS_KEY  values.yaml
fill_template "<minio_secret_key>" $MINIO_SECRET_KEY values.yaml
helm dep up .
helm install --name $RELEASE_NAME .
FAILED=$?
show_result "$FAILED" "Minio storage installed" "Failed to install Minio storage"
cd -
cp minio_ing_tmpl.yaml minio_ing.yaml
fill_template "<minio_external_uri>" $MINIO_EXTERNAL_URI minio_ing.yaml
fill_template "<minio_service>" $RELEASE_NAME minio_ing.yaml
kubectl create -f minio_ing.yaml
FAILED=$?
show_result "$FAILED" "Minio ingress created at $MINIO_EXTERNAL_URI" "Failed to install Minio ingress"

