#!/usr/bin/env bash
MINIO_ENDPOINT="minioplatform.default:9000"
MINIO_URL="http://$MINIO_ENDPOINT"
helm install --set minio.endpoint=$MINIO_ENDPOINT --set minio.endpointUrl=$MINIO_URL --set minio.accessKey=$MINIO_ACCESS_KEY --set minio.secretKey=$MINIO_SECRET_KEY --set image=$CRD_IMAGE --set tag=$CRD_TAG --set platformDomain=$DOMAIN_NAME ../../helm-deployment/crd-subchart/
