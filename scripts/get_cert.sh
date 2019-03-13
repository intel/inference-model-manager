#!/bin/bash
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

ADDRESS=$1
SUBJECT=$2
PROXY=$3

sleep 10
if [ ! -z "$PROXY" ]; then
    proxytunnel -p $PROXY -d $ADDRESS:443 -a 7000 &
    openssl s_client -connect localhost:7000 -servername $ADDRESS -showcerts  < /dev/null 2>/dev/null |grep "s:.*CN.*${SUBJECT}" -A 100 | openssl x509 -outform pem
    kill `ps -ef | grep proxytunnel | awk '{print $2}'`
else
    openssl s_client -connect $ADDRESS:443 -servername $ADDRESS -showcerts  < /dev/null 2>/dev/null | grep "s:.*CN.*${SUBJECT}" -A 100|  openssl x509 -outform pem
fi

