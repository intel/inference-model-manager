#!/usr/bin/env bash
helm dep up ../../helm-deployment/minio-subchart/
helm install --name minioplatform --set minio.accessKey=$MINIO_ACCESS_KEY --set minio.secretKey=$MINIO_SECRET_KEY ../../helm-deployment/minio-subchart/
