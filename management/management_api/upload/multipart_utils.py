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
    return f"{body['modelName']}-{body['modelVersion']}/0/{body['fileName']}"
