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

sudo chmod u+s `which ping`
sudo setcap cap_net_raw+p /bin/ping

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
  cd ~/inference-model-manager/installer/utils/route53/
  virtualenv .venvaws -p python3
  . .venvaws/bin/activate
  pip install awscli --upgrade 
  export AWS_DNS=`./apply.sh CREATE $EXTERNAL_IP ${CLUSTER_NAME_SHORT}.nlpnp.adsdcsp.com`
  cat route_record.json
  export AWS_DNS_ID=$(echo $AWS_DNS | jq '.ChangeInfo.Id')
  echo ${AWS_DNS_ID} 
  sleep 30
  while [ "$STATUS" = "INSYNC" ]; do sleep 10; export STATUS=$(aws route53 get-change --id `echo ${AWS_DNS_ID} | tr -d "\""` | jq '.ChangeInfo.Status'); echo $STATUS; done
  deactivate
  success "DNS records update confirmed"
  cd -
else
  success "DNS entry already present"      
fi
