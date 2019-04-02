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
helm_arr=()
K8S_NS_ARR=()

CERTS_PATH="`pwd`/certs/$IMM_RELEASE_PREFIX"
cd ../scripts
LIST_TENANTS_RESPONSE=`./imm ls t`

if [[ "$LIST_TENANTS_RESPONSE" =~ "Token not valid" ]]; then
        echo "Uninstallation aborted. Your token is invalid, please log in and try again."
else
    while read i; do
        RELEASE_NAME=`jq --arg namearg "Name" '.[$namearg]' <<< $i | tr -d '"'`
        mark_release_to_be_deleted $RELEASE_NAME
    done <<<"$(jq -c '.[]' <<< $HELM_LIST)"

    [[ $LIST_TENANTS_RESPONSE =~ '['(.*)']' ]] &&
        tenants=`echo ${BASH_REMATCH[1]} | tr -d "\""`
    IFS=', ' read -r -a tenants_arr <<< "$tenants"

    if [[ "$quiet" != "yes" ]]; then
        echo "Uninstalling IMM. Following components will be removed:"
        echo "*Helm releases:"
        for release in "${helm_arr[@]}"; do echo "    - $release" ; done
        echo "*Tenants with theirs resources(models,endpoints etc.):"
        for tenant in "${tenants_arr[@]}"; do echo "    - $tenant" ; done
        echo "Are you sure you want to uninstall IMM? y/N"
        read DELETE_IMM
    else
        DELETE_IMM="y"
    fi
    if [[ $DELETE_IMM == "y" ]]; then
        error=0
        echo "Deleting tenants..."
        for tenant in "${tenants_arr[@]}"; do
            DELETE_TENANT_RESULT=`./imm -k rm t $tenant`
            if [[ !("$DELETE_TENANT_RESULT" =~ "DELETED") ]]; then
                error=1
            fi
            echo $DELETE_TENANT_RESULT
        done

        if [[ $error == 0 ]]; then
            echo "Deleting helm releases..."
            cd ../installer
            for i in "${helm_arr[@]}"; do
                HELM_OUTPUT=$((helm del --purge $i) 2>&1)
                echo $HELM_OUTPUT
                if [[ $HELM_OUTPUT =~ E|error ]]; then
                    error=1
                fi
            done
        fi

        if [[ $error == 0 ]]; then
            echo "Deleting minio-ingress..."
            KUBECTL_OUTPUT=$((kubectl delete ing minio-ingress) 2>&1)
            echo $KUBECTL_OUTPUT
            if [[ $KUBECTL_OUTPUT =~ E|error ]]; then
                error=1
            fi
        fi
        if [[ $error == 0 ]]; then
            if [[ "$quiet" != "yes" ]]; then
                echo "Do you want to delete certificates under $CERTS_PATH? y/N"
                read DELETE_CERTS
            else
                DELETE_CERTS="y"
            fi
            if [[ $DELETE_CERTS == "y" ]]; then
                echo "Deleting certificates..."
                CERT_RM_OUTPUT=$((rm -rf $CERTS_PATH) 2>&1)
                echo $CERT_RM_OUTPUT
                if [[ $CERT_RM_OUTPUT =~ E|error ]]; then
                    error=1
                fi
            fi
        fi

        if [[ $error == 0 ]]; then
            echo "IMM uninstalled successfully."
        else
            echo "IMM uninstallation failed. Not all components have been deleted."
        fi
    else
        echo "Quiting uninstaller."
    fi
fi
