from management_api.config import minio_client
from botocore.exceptions import ClientError
from management_api.utils.errors_handling import MinioCallException


def create_upload(bucket: str, key: str):
    try:
        mpu = minio_client.create_multipart_upload(Bucket=bucket, Key=key)
    except ClientError as clientError:
        raise MinioCallException('An error occurred during multipart upload starting: {}'.
                                 format(clientError))
    mpu_id = mpu["UploadId"]
    return mpu_id


def upload_part(data: bytes, part_number: int, bucket: str, key: str, multipart_id: str):
    try:
        minio_client.upload_part(Body=data, PartNumber=part_number,
                                 Bucket=bucket, Key=key, UploadId=multipart_id)
    except ClientError as clientError:
        raise MinioCallException('An error occurred during part uploading: {}'.
                                 format(clientError))


def complete_upload(bucket: str, key: str, multipart_id: str):
    try:
        minio_client.complete_multipart_upload(Bucket=bucket, Key=key, UploadId=multipart_id)
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
    return "{model_name}/{model_version}".format(model_name=body['modelName'],
                                                 model_version=body['modelVersion'])
