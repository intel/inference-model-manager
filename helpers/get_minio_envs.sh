#!/usr/bin/env bash

#use when you already have management-api and minio k8s deployments

MINIO_IP=`kubectl get svc | grep minio | awk '{print $4}'`
MINIO_PORT=`kubectl get svc | grep minio | awk '{print $5}' | awk -F ':' '{print $1}'`
export MINIO_ENDPOINT=http://${MINIO_IP}:${MINIO_PORT}
echo ${MINIO_ENDPOINT}

MINIO_POD=`kubectl get pod | grep minio | awk '{print $1}'`
export `kubectl exec -it ${MINIO_POD} env | grep 'MINIO_SECRET_KEY='`
echo ${MINIO_SECRET_KEY}

export `kubectl exec -it ${MINIO_POD} env | grep 'MINIO_ACCESS_KEY='`
echo ${MINIO_ACCESS_KEY}