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

[[ $OSTYPE == "darwin"* ]] && EXTERNAL_IP=`kubectl get services -n ingress-nginx|grep ingress-nginx|awk '{print $4}'` \
                           || EXTERNAL_IP=`kubectl get services -n ingress-nginx|grep ingress-nginx|awk '{print $3}'`
success "External ip found: $EXTERNAL_IP"
sleep 5
done

header "Waiting in the loop for updated dns records"
result=""
wait_time=0
while [ -z "$result" ]
do         
  action_required  "Please update DNS records for domain $DOMAIN_NAME to point $EXTERNAL_IP"
  result=`ping something.$DOMAIN_NAME -c 1 2>&1|grep $EXTERNAL_IP`
  sleep 5
  wait_time=$(($wait_time + 5))
  print_ne "\r\r\r\r\r\r\r\r\r\r\r\r elapsed time: $wait_time s"
done
success "DNS records update confirmed"
