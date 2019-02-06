#!/bin/bash
CLUSTER_NAME=$1
DNS_DOMAIN_NAME=$2
export SED_CMD="gsed"
export ISSUER=https://dex.$DNS_DOMAIN_NAME:443/dex # change 443 port if using kubernetes node port instead of load balancer
export DEX_NAMESPACE=dex


./restart_k8sapi.sh $CLUSTER_NAME $ISSUER $DEX_NAMESPACE


