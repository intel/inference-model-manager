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

delete_release_if_included_in_list() {
    chart_name=$1
    release_name=$2
    [[ $CHARTS_LIST =~ (^|[[:space:]])$chart_name($|[[:space:]]) ]] && echo "Release will be deleted" && helm del --debug --purge $release_name || echo 'Release wont be deleted'
}

CHARTS_LIST="imm-management-api-chart imm-crd-subchart imm-openldap imm-dex-subchart imm-ingress minio"
HELM_LS_OUTPUT=`helm ls --output json`
HELM_LIST=`jq --arg namearg "Releases" '.[$namearg]' <<< $HELM_LS_OUTPUT`


jq -c '.[]' <<< $HELM_LIST | while read i; do
   echo "Chart metadata: $i"
   CHART_NAME=`jq --arg namearg "Chart" '.[$namearg]' <<< $i | tr -d '"' | tr -d '.0123456789' | rev | cut -c 2- | rev`
   RELEASE_NAME=`jq --arg namearg "Name" '.[$namearg]' <<< $i | tr -d '"'`
   delete_release_if_included_in_list $CHART_NAME $RELEASE_NAME
done
