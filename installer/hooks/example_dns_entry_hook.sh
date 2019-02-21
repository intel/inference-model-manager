#!/bin/bash
IP_ADDRESS=$1
DOMAIN_NAME=$2
cd ../utils/route53
./apply.sh CREATE $IP_ADDRESS $DOMAIN_NAME
cd -
