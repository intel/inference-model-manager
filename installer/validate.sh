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
#!/bin/bash

. ./utils/messages.sh

DOMAIN_NAME=$1
PROXY=$2
cd ../scripts
header "Validating IMM platform installation"
header "Preparing python environment"
[[ ! -d .testenv ]] && virtualenv -p python3.6 .testvenv
. .testvenv/bin/activate
pip install -r requirements.txt
header "Preparing env variables and installing CA"
. ./prepare_test_env.sh $DOMAIN_NAME $PROXY
header "Running tests"
./test_imm.sh
deactivate
cd -
