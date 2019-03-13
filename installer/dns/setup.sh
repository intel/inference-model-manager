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

DOMAIN_NAME=$1
EXTERNAL_IP="<pending>"
header "Waiting for external ip address"
while [ ! -z "x" ]
do
if  [[ "$EXTERNAL_IP" != "<pending>" ]]
then
  break
fi

EXTERNAL_IP=`kubectl get services -n ingress-nginx|grep ingress-nginx|awk '{ print $(NF-2) }'` 
sleep 5
done

success "External ip found: $EXTERNAL_IP"
result=`ping dex.$DOMAIN_NAME -c 1 2>&1|grep $EXTERNAL_IP`

if [ -z "$result" ]; then
  
  if [ -f "../hooks/dns_entry_hook.sh" ]; then
    header "Found hook script for DNS entry, setting $DOMAIN_NAME to $EXTERNAL_IP"
    ../hooks/dns_entry_hook.sh $EXTERNAL_IP $DOMAIN_NAME
  else        
    action_required  "Please update DNS records for domain $DOMAIN_NAME to point $EXTERNAL_IP"
  fi

  header "Waiting in the loop for updated dns records"
  result=""
  wait_time=0
  while [ -z "$result" ]
  do
    export check=`ping foo.$DOMAIN_NAME -c 1 2>&1`
    echo $check         
    export result=`ping foo.$DOMAIN_NAME -c 1 2>&1|grep $EXTERNAL_IP`
    echo $result
    sleep 20
    wait_time=$(($wait_time + 20))
    print_ne "\r\r\r\r\r\r\r\r\r\r\r\r elapsed time: $wait_time s"
  done
  success "DNS records update confirmed"

else
  success "DNS entry already present"      
fi
