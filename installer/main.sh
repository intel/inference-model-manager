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

echo "All args:[ $@ ]"

DESIRED_KOPS_CLUSTER_NAME=$1
DNS_DOMAIN_NAME=$2
GCE_ZONE=$3
MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY:=my_minio_key}"
MINIO_SECRET_KEY="${MINIO_SECRET_KEY:=my_minio_secret}"
MINIO_SIGNATURE="${MINIO_SIGNATURE:=s3v4}"
MINIO_REGION="${MINIO_REGION:=us-east-1}"
RELEASE_PREFIX="${RELEASE_PREFIX:=imm}"

if [[ -z "${MINIO_URL}" ]]; then
  MINIO_URL="http://minio.$DNS_DOMAIN_NAME"
  INSTALL_MINIO="true"
else
  INSTALL_MINIO="false"
fi

if [[ $MINIO_URL =~ ^https ]];
then
    export USE_HTTPS=1
else
    export USE_HTTPS=0
fi

if [ -z $MGMT_IMAGE ]; then
    export MGMT_IMAGE=intelaipg/inference-model-manager-api
fi
if [ -z $CRD_IMAGE ]; then
    export CRD_IMAGE=intelaipg/inference-model-manager-crd
fi
if [ -z $MGMT_TAG ]; then
    export MGMT_TAG=latest
fi
if [ -z $CRD_TAG ]; then
    export CRD_TAG=latest
fi


export ISSUER=https://dex.$DNS_DOMAIN_NAME:443/dex # change 443 port if using kubernetes node port instead of load balancer
export DEX_NAMESPACE=dex
export DEX_DOMAIN_NAME=dex.$DNS_DOMAIN_NAME
export DOMAIN_NAME=$DNS_DOMAIN_NAME
export HELM_TEMP_DIR=`pwd`/helm-temp-dir

if [ -z $MGT_API_AUTHORIZATION ]; then
    export MGT_API_AUTHORIZATION="false"
fi

if [[ ! -d ../.venv ]]; then
    virtualenv -p python3.6 ../.venv
    . ../.venv/bin/activate
    pip install -q --upgrade pip &&  pip install -q -r ../tests/requirements.txt && pip install -q -r ../scripts/requirements.txt
fi

cd ..
rm -fr $HELM_TEMP_DIR
cp -r helm-deployment $HELM_TEMP_DIR
cd -


. utils/validate_envs.sh

. utils/progress_bar.sh
. utils/wait_for_pod.sh
. utils/messages.sh


if [ ! -z "$DESIRED_KOPS_CLUSTER_NAME" ] && [ -z "$SKIP_K8S_INSTALLATION" ]; then
    cd k8s
    . create_kops_cluster_gke.sh $DESIRED_KOPS_CLUSTER_NAME $GCE_ZONE
    . install_tiller.sh
    cd ..
fi

cd ingress
. install.sh $RELEASE_PREFIX
cd ..

cd crd
. install.sh $DNS_DOMAIN_NAME $USE_HTTPS $RELEASE_PREFIX
cd ..

cd dns
. setup.sh $DNS_DOMAIN_NAME
cd ..

if [[ "$INSTALL_MINIO" == "true" ]]; then
    cd minio
    . install.sh $MINIO_ACCESS_KEY $MINIO_SECRET_KEY $MINIO_URL $RELEASE_PREFIX
    cd ..
fi

cd ldap
. install.sh $RELEASE_PREFIX
cd ..

cd dex
. install.sh $ISSUER $DEX_NAMESPACE $DEX_DOMAIN_NAME $RELEASE_PREFIX
cd ..

if [ "$MGT_API_AUTHORIZATION" == "false" ]; then
        if [[ ! -z "$DESIRED_KOPS_CLUSTER_NAME" ]] && [[ -z "$SKIP_K8S_INSTALLATION" ]]; then
                cd k8s
                . ./restart_k8sapi.sh $DESIRED_KOPS_CLUSTER_NAME $ISSUER $DEX_NAMESPACE
                cd ..
        else
                cd k8s
                DEX_CA=`./get_ing_ca_crt.sh`
                action_required "Please restart K8S API with OIDC config:\n oidcIssuerURL: $ISSUER: \noidcCA: $DEX_CA\noidcClientID: example-app\noidcGroupsClaim: groups\noidcUsernameClaim: email"
                read -p "Press [ENTER] when ready"
                cd -
        fi
fi

cd management-api
. ./install.sh $DOMAIN_NAME $MINIO_ACCESS_KEY $MINIO_SECRET_KEY $MINIO_URL $MINIO_REGION $MINIO_SIGNATURE $MGT_API_AUTHORIZATION $RELEASE_PREFIX
show_result $? "Done" "Aborting"
cd ..

cd ../scripts
header "Preparing env variables and installing CA"
sleep 10
. ./prepare_test_env.sh $DOMAIN_NAME $PROXY
cd -

if [[ -n $DEFAULT_TENANT_NAME ]]; then
    echo "Creating default tenant"
    . default_tenant.sh $DOMAIN_NAME $PROXY
fi

if [[ ! -n $SKIP_VALIDATION ]]; then
. validate.sh
else
    success "If you want to run tests please run:\n . ./prepare_test_env.sh $DOMAIN_NAME $PROXY\n . validate.sh\n"
fi
