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

mark_release_to_be_deleted() {
    release_name=$1
    [[ $CHARTS_LIST =~ (^|[[:space:]])$release_name($|[[:space:]]) ]] && helm_arr+=("$release_name")
}

IMM_RELEASE_PREFIX="${IMM_RELEASE_PREFIX:=imm}"

while getopts "qf:l:" opt; do
    case "$opt" in
    f)  export IMM_RELEASE_PREFIX=$OPTARG
        ;;
    q)  quiet="yes"
        ;;
    esac
done

shift $((OPTIND-1))


CHARTS_LIST="$IMM_RELEASE_PREFIX-mgt-api $IMM_RELEASE_PREFIX-crd $IMM_RELEASE_PREFIX-dex $IMM_RELEASE_PREFIX-ingress $IMM_RELEASE_PREFIX-openldap $IMM_RELEASE_PREFIX-minio"
HELM_LS_OUTPUT=`helm ls --output json`
HELM_LIST=`jq --arg namearg "Releases" '.[$namearg]' <<< $HELM_LS_OUTPUT`
K8S_NS_OUTPUT=`kubectl get ns --output=json`
K8S_NS_LIST=`jq --arg namearg "items" '.[$namearg]' <<< $K8S_NS_OUTPUT`
helm_arr=()
K8S_NS_ARR=()

cd ../scripts
./imm -k rm t default-tenant
rm -rf ./certs/$IMM_RELEASE_PREFIX
cd ../installer

while read i; do
   echo $i
   RELEASE_NAME=`jq --arg namearg "Name" '.[$namearg]' <<< $i | tr -d '"'`
   mark_release_to_be_deleted $RELEASE_NAME
done <<<"$(jq -c '.[]' <<< $HELM_LIST)"


echo "Releases marked to be deleted:"

for i in "${helm_arr[@]}"; do echo "$i" ; done

if [[ "$quiet" == "yes" ]]; then
    for i in "${helm_arr[@]}"; do helm del --debug --purge $i ; done
else
    read -p "Do you want to delete helm releases listed above Y/n?" DELETE_CHARTS
    [[ $DELETE_CHARTS != "n" ]] && for i in "${helm_arr[@]}"; do helm del --debug --purge $i ; done
fi

kubectl delete ing minio-ingress || true
