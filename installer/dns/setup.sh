#!/bin/bash
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
    result=`ping foo.$DOMAIN_NAME -c 1 2>&1|grep $EXTERNAL_IP`
    sleep 20
    wait_time=$(($wait_time + 20))
    print_ne "\r\r\r\r\r\r\r\r\r\r\r\r elapsed time: $wait_time s"
  done
  success "DNS records update confirmed"

else
  success "DNS entry already present"      
fi
