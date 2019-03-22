#!/usr/bin/env bash
#
# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
B64DECODE="${B64DECODE:=base64 --decode}"
RETURN_DIR=$PWD
if [ "$MGMT_CERTS" = "true" ]; then
    echo "External mgmt-api self-signed certs will be generated for DNS ${MGMT_DOMAIN_NAME}"
    cd ../../helm-deployment/management-api-subchart/certs/ && ./generate-ing-management-api-certs.sh
    cd $RETURN_DIR
fi
if [ "$MGMT_INTERNAL_CERTS" = "true" ]; then
    echo "Internal mgmt-api certs will be generated"
    cd ../../helm-deployment/management-api-subchart/certs/ && ./generate-management-api-certs.sh
    cd $RETURN_DIR
fi
kubectl get secret -n dex ca-secret-dex -o yaml | yq r - 'data."ca.crt"' | $B64DECODE > ../../helm-deployment/management-api-subchart/certs/ca-dex.crt
MINIO_ENDPOINT="minio.default:9000"
MINIO_URL="http://$MINIO_ENDPOINT"
helm install --set image=$MGMT_IMAGE --set tag=$MGMT_TAG --set platformDomain=$DOMAIN_NAME \
--set dexExternalURL=dex.${DOMAIN_NAME}:443 --set ingress.hosts=${MGMT_DOMAIN_NAME} \
--set ingress.tls.hosts=${MGMT_DOMAIN_NAME} --set minio.endpoint=$MINIO_ENDPOINT \
--set minio.endpointUrl=$MINIO_URL --set minio.accessKey=$MINIO_ACCESS_KEY \
--set minio.minioRegion="us-east-1" --set minio.minioSignatureVersion="s3v4" \
--set minio.secretKey=$MINIO_SECRET_KEY ../../helm-deployment/management-api-subchart/ \
--set automountServiceAccountToken=false \
--set useMgtApiAuthorization=false
