#!/usr/bin/env bash

MANAGEMENT_IP=`kubectl get svc -l "run=management-api" -o "jsonpath={$.items[0].status.loadBalancer.ingress[0].ip}"`
export MANAGEMENT_API_URL='http://'"${MANAGEMENT_IP}"':5000/tenants'
echo $MANAGEMENT_API_URL

MINIO_SECRET_KEY=`kubectl get secret minio-access-info -o 'go-template={{index .data "minio.access_secret_key"}}' | base64 -d`
echo $MINIO_SECRET_KEY

MINIO_ACCESS_KEY=`kubectl get secret minio-access-info -o 'go-template={{index .data "minio.access_key_id"}}' | base64 -d`
echo $MINIO_ACCESS_KEY

export MINIO_ENDPOINT_ADDR='http://127.0.0.1:9000'
export MINIO_POD=`kubectl get pod | grep minio | awk '{print $1}'`
kubectl port-forward ${MINIO_POD} 9000:9000 &

pytest -v 

pkill -f "port-forward"
