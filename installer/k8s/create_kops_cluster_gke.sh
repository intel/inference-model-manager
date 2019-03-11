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

. ../utils/progress_bar.sh
. ../utils/fill_template.sh
. ../utils/messages.sh
```
#### Create cluster
```

header "Installing kubernetes cluster"

CLUSTER_NAME=$1
GCE_REGION=$2
cp ../../kops/desiredcni.yaml ./cluster.yaml
fill_template toreplacebyclustername $CLUSTER_NAME cluster.yaml
fill_template us-west1 ${GCE_REGION} cluster.yaml
kops create -f cluster.yaml
kops update cluster $CLUSTER_NAME.k8s.local --yes
show_result $? "Kubernetes cluster created" "Failed to create cluster" 
echo "Waiting 300 seconds for cluster to be ready"
progress_bar 300
header "Installing weave"
kubectl create -f https://git.io/weave-kube-1.6
show_result $? "Weave installed" "Failed to install weave"
