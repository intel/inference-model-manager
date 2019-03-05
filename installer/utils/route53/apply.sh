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

OP=$1 # CREATE, UPSERT, DELETE
IP_ADDR=$2
DOMAIN=$3
SED_CMD=sed
if [ "$(uname)" == "Darwin" ]; then
        SED_CMD=gsed
fi   

cp route_record_tmpl.json route_record.json
$SED_CMD -i "s/<operation>/$OP/g" route_record.json
$SED_CMD -i "s/<ip_address>/$IP_ADDR/g" route_record.json
$SED_CMD -i "s/<dns_domain_name>/$DOMAIN/g" route_record.json
echo "Created Route53 config:"
cat route_record.json
[[ ! -d .venvaws ]] && virtualenv .venvaws -p python3
. .venvaws/bin/activate
pip install awscli --upgrade 
aws route53 change-resource-record-sets --hosted-zone-id Z11DOV0M5AJEBB --change-batch file://./route_record.json
deactivate

