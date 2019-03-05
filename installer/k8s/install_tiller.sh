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

. ../utils/wait_for_pod.sh
. ../utils/progress_bar.sh
. ../utils/messages.sh

header "Installing tiller on k8s"

kubectl -n kube-system create serviceaccount tiller

kubectl create clusterrolebinding tiller \
  --clusterrole cluster-admin \
  --serviceaccount=kube-system:tiller

helm init --service-account tiller
show_result $? "Tiller installed" "Failed to install tiller"
echo "Waiting for tiller pod to be ready"
wait_for_pod 300 tiller-deploy kube-system
# extra wait because presence of tiller is not enough
echo "Extra wait for 30s"
progress_bar 30


