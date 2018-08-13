#!/usr/bin/env bash

MANAGEMENT_IP=`kubectl get svc | grep management | awk '{print $4}'`
export MANAGEMENT_API_URL='http://'${MANAGEMENT_IP}':5000/tenants'
echo 'export MANAGEMENT_API_URL='${MANAGEMENT_API_URL}

MINIO_POD=`kubectl get pod | grep minio | awk '{print $1}'`
MINIO_SECRET=`kubectl exec -it ${MINIO_POD} env | grep 'MINIO_SECRET_KEY=' | awk -F \
'=' '{print $2}'`
export MINIO_SECRET_KEY=${MINIO_SECRET}
echo 'export MINIO_SECRET_KEY='${MINIO_SECRET_KEY}

MINIO_ACCESS=`kubectl exec -it ${MINIO_POD} env | grep 'MINIO_ACCESS_KEY=' | awk -F \
'=' '{print $2}'`
export MINIO_ACCESS_KEY=${MINIO_ACCESS}
echo 'export MINIO_ACCESS_KEY='${MINIO_ACCESS_KEY}

MINIO_IP=`kubectl describe pod ${MINIO_POD} | grep IP | awk '{print $2}'`
MINIO_ENDPOINT='http://'${MINIO_IP}':9000'
export MINIO_ENDPOINT_ADDR=${MINIO_ENDPOINT}
echo 'export MINIO_ENDPOINT_ADDR='${MINIO_ENDPOINT_ADDR}
