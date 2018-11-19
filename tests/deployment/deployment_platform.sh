#!/usr/bin/env bash


echo "deploy ingress"
source ./deployment_ingress.sh
echo "deploy CRD"
source ./deployment_crd.sh
echo "deploy minio"
source ./deployment_minio.sh
echo "deploy dex"
source ./deployment_dex.sh
echo "deploy management api"
source ./deployment_management_api.sh
