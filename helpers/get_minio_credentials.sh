#!/usr/bin/env bash

export MINIO_ACCESS_KEY_ID=`cat ~/.minio/config.json | grep accessKey | awk '{print substr($2, 2, length($2)-3)}'`
echo ${MINIO_ACCESS_KEY_ID}
export MINIO_SECRET_ACCESS_KEY=`cat ~/.minio/config.json | grep secretKey | awk '{print substr($2, 2, length($2)-2)}'`
echo ${MINIO_SECRET_ACCESS_KEY}