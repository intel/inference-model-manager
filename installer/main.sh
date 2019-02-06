#!/bin/bash
CLUSTER_NAME=$1
REGISTRY_URL="gcr.io/constant-cubist-173123/"
CRD_IMAGE_NAME="server-controller-prod"
IMAGES_TAG="latest"
DNS_DOMAIN_NAME=$2
#"kops-test.nlpnp.adsdcsp.com"
MINIO_ACCESS_KEY="my_minio_key"
MINIO_SECRET_KEY="my_minio_secret"
MINIO_URL=minio.$DNS_DOMAIN_NAME

export ISSUER=https://dex.$DNS_DOMAIN_NAME:443/dex # change 443 port if using kubernetes node port instead of load balancer
export DEX_NAMESPACE=dex
export DEX_DOMAIN_NAME=dex.$DNS_DOMAIN_NAME
export DOMAIN_NAME=$DNS_DOMAIN_NAME

echo "All args:[ $@ ]"
#SKIP_K8S_INSTALL="yes"

. utils/validate_envs.sh
. utils/progress_bar.sh
. utils/wait_for_pod.sh

if [ -z "$SKIP_K8S_INSTALL" ]; then
cd k8s
. create_cluster.sh $CLUSTER_NAME 
. install_tiller.sh 
cd ..
fi

cd ingress
. install.sh
cd ..

cd crd
. install.sh $REGISTRY_URL $CRD_IMAGE_NAME $IMAGES_TAG $DNS_DOMAIN_NAME
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

if [ -z "$SKIP_K8S_INSTALL" ]; then
cd k8s
. ./restart_k8sapi.sh $CLUSTER_NAME $ISSUER $DEX_NAMESPACE 
cd ..
fi

cd mgtapi
. ./install.sh $DOMAIN_NAME $MINIO_ACCESS_KEY $MINIO_SECRET_KEY $MINIO_URL 
cd ..


