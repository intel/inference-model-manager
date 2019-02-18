#!/bin/bash
CLUSTER_NAME=$1
DNS_DOMAIN_NAME=$2
GCE_ZONE=$3
#"kops-test.nlpnp.adsdcsp.com"
MINIO_ACCESS_KEY="my_minio_key"
MINIO_SECRET_KEY="my_minio_secret"
MINIO_URL=minio.$DNS_DOMAIN_NAME

export ISSUER=https://dex.$DNS_DOMAIN_NAME:443/dex # change 443 port if using kubernetes node port instead of load balancer
export DEX_NAMESPACE=dex
export DEX_DOMAIN_NAME=dex.$DNS_DOMAIN_NAME
export DOMAIN_NAME=$DNS_DOMAIN_NAME

echo "All args:[ $@ ]"

. utils/validate_envs.sh
. utils/progress_bar.sh
. utils/wait_for_pod.sh

if [ -z "$SKIP_K8S_INSTALLATION" ]; then
    cd k8s
    . create_cluster.sh $CLUSTER_NAME $GCE_ZONE
    . install_tiller.sh 
    cd ..
fi

cd ingress
. install.sh
cd ..

cd crd
. install.sh 
cd ..

cd dns
. setup.sh $DNS_DOMAIN_NAME 
cd ..

cd minio
. install.sh $MINIO_ACCESS_KEY $MINIO_SECRET_KEY $MINIO_URL
cd ..

cd ldap
. install.sh
cd ..

cd dex
. install.sh $ISSUER $DEX_NAMESPACE $DEX_DOMAIN_NAME
cd .. 

pwd 

cd validate
.  ./test_dex_ldap.sh https://$DEX_DOMAIN_NAME
cd ..

if [ -z "$SKIP_K8S_INSTALLATION" ]; then
    cd k8s
    . ./restart_k8sapi.sh $CLUSTER_NAME $ISSUER $DEX_NAMESPACE 
    cd ..
fi

cd mgtapi
. ./install.sh $DOMAIN_NAME $MINIO_ACCESS_KEY $MINIO_SECRET_KEY $MINIO_URL 
cd ..


