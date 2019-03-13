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

. ../utils/messages.sh
. ../utils/wait_for_pod.sh
header "Installing ingress controller"
cd $HELM_TEMP_DIR/ing-subchart
helm install .
header "Waiting for ingress controller pod"
wait_for_pod 60 nginx-ingress-controller ingress-nginx
cd -
