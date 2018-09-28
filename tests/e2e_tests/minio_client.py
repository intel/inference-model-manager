import logging


def copy(minio_client, src_bucket, dest_bucket, src_key, dest_key):
    copy_source = f"{src_bucket}/{src_key}"
    try:
        response = minio_client.copy_object(Bucket=dest_bucket, CopySource=copy_source,
                                            Key=dest_key)
    except Exception as e:
        logging.error('An error occurred during minio copy: {}'.format(e))
    return response
