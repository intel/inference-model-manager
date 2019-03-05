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
export PROJECT=`gcloud config get-value project`
export KOPS_FEATURE_FLAGS=AlphaAllowGCE
export KOPS_STATE_STORE=gs://kubernetes-clusters-imm
```

#### Update cluster

```
CLUSTER_NAME=$1
ISSUER=$2
DEX_NAMESPACE=$3

header "Restarting k8s api with params: cluster name: $CLUSTER_NAME issuer: $ISSUER dex namespace: $DEX_NAMESPACE"

cp oidc_tmpl.yaml oidc.yaml

fill_template toreplacebyissuer $ISSUER oidc.yaml

DEX_ING_CA=`./get_ing_ca_crt.sh`
echo "Found certificate: $DEX_ING_CA"
echo "$DEX_ING_CA" > ca-ing.crt
${SED_CMD} -i -e 's/^/      /' ca-ing.crt 
${SED_CMD} -i -e '/replacebycertificate/{r ca-ing.crt' -e 'd}' oidc.yaml
OIDC_CFG=`cat oidc.yaml`

kops get cluster --name $CLUSTER_NAME.k8s.local --output json > config.yaml
yq m config.yaml oidc.yaml > config_oidc.yaml
cat config_oidc.yaml
kops replace -f config_oidc.yaml 
header "Configuration updated, restarting cluster"
kops update cluster --yes 
kops rolling-update cluster --yes
show_result $? "Restart succeded" "Restart failed"

