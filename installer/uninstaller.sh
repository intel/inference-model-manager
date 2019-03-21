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

charts_list="management-api-chart crd-subchart openldap dex-subchart ingress"
HELM_OUTPUT=`helm ls --output json`
HELM_LIST=`jq --arg namearg "Releases" '.[$namearg]' <<< $HELM_OUTPUT`
jq -c '.[]' <<< $HELM_LIST | while read i; do
   echo "Chart metadata: $i"
   chart_name=`jq --arg namearg "Chart" '.[$namearg]' <<< $i | tr -d '"' | tr -d '.0123456789' | rev | cut -c 2- | rev`
   release_name=`jq --arg namearg "Name" '.[$namearg]' <<< $i | tr -d '"'`
   [[ $charts_list =~ (^|[[:space:]])$chart_name($|[[:space:]]) ]] && echo "Release will be deleted" && helm del --debug --purge $release_name || echo 'Release wont be deleted'
done
