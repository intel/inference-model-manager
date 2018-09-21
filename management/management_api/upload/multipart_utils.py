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
