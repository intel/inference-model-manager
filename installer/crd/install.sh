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

header "Installation of CRD Controller"
DOMAIN_NAME=$1
USE_HTTPS=$2
cd $HELM_TEMP_DIR/crd-subchart
fill_template "<crd_image>" $CRD_IMAGE values.yaml
fill_template "<crd_tag>" $CRD_TAG values.yaml
fill_template "<dns_domain_name>" $DOMAIN_NAME values.yaml
fill_template "<use_https>" $USE_HTTPS values.yaml
helm install .
show_result $? "CRD installation completed" "Failed to install CRD"
cd -
