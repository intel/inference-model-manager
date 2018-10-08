#!/usr/bin/env bash

MANAGEMENT_IP=`kubectl get svc -l "run=management-api" -o "jsonpath={$.items[0].status.loadBalancer.ingress[0].ip}"`
export MANAGEMENT_API_URL='http://'"${MANAGEMENT_IP}"':5000'
echo "URL FOR MANAGEMENT API: $MANAGEMENT_API_URL"

DEX_SERVICE=`kubectl get svc|grep "dex   "| awk '{ print $1 }'`
DEX_IP=`kubectl get svc "$DEX_SERVICE" -o "jsonpath={$.status.loadBalancer.ingress[0].ip}"`
export DEX_URL='https://'"${DEX_IP}"':443'
echo "URL FOR DEX :  $DEX_URL"


MINIO_SECRET_KEY=`kubectl get secret minio-access-info -o 'go-template={{index .data "minio.access_secret_key"}}' | base64 -d`
echo $MINIO_SECRET_KEY

MINIO_ACCESS_KEY=`kubectl get secret minio-access-info -o 'go-template={{index .data "minio.access_key_id"}}' | base64 -d`
echo $MINIO_ACCESS_KEY

export MINIO_ENDPOINT_ADDR='http://127.0.0.1:9000'
export MINIO_POD=`kubectl get pod | grep minio | awk '{print $1}'`
kubectl port-forward ${MINIO_POD} 9000:9000 &

pytest -v

echo "Stop port forwarding"
pkill -e -f "port-forward"
echo "Pkill succeded"
exit 0
