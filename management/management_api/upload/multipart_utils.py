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

from management_api.config import minio_client
from botocore.exceptions import ClientError
from management_api.utils.errors_handling import MinioCallException


def create_upload(bucket: str, key: str):
    response = None
    try:
        response = minio_client.create_multipart_upload(Bucket=bucket, Key=key)
    except ClientError as clientError:
        raise MinioCallException('An error occurred during multipart upload starting: {}'.
                                 format(clientError))
    return response['UploadId']


def upload_part(data: bytes, part_number: int, bucket: str, key: str, multipart_id: str):
    response = None
    try:
        response = minio_client.upload_part(Body=data, PartNumber=part_number,
                                            Bucket=bucket, Key=key, UploadId=multipart_id)
    except ClientError as clientError:
        raise MinioCallException('An error occurred during part uploading: {}'.
                                 format(clientError))
    return response['ETag']


def complete_upload(bucket: str, key: str, multipart_id: str, parts: list):
    try:
        minio_client.complete_multipart_upload(Bucket=bucket, Key=key, UploadId=multipart_id,
                                               MultipartUpload={'Parts': parts})
    except ClientError as clientError:
        raise MinioCallException('An error occurred during multipart upload finishing: {}'.
                                 format(clientError))


def abort_upload(bucket: str, key: str, multipart_id: str):
    try:
        minio_client.abort_multipart_upload(Bucket=bucket, Key=key, UploadId=multipart_id)
    except ClientError as clientError:
        raise MinioCallException(f'An error occurred during multipart upload abortion: '
                                 f'{clientError}')


def get_key(body):
    return f"{body['modelName']}/{body['modelVersion']}/{body['fileName']}/{body['key']}"
