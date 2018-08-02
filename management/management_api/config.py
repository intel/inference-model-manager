import boto3
import os
from botocore.client import Config
from kubernetes import config, client

HOSTNAME = os.getenv('HOSTNAME', 'localhost')
PORT = int(os.getenv('PORT', 5000))
MINIO_ACCESS_KEY_ID = os.environ['MINIO_ACCESS_KEY_ID']
MINIO_SECRET_ACCESS_KEY = os.environ['MINIO_SECRET_ACCESS_KEY']
MINIO_ENDPOINT_ADDR = os.getenv('MINIO_ENDPOINT_ADDR', 'http://127.0.0.1:9000')

MINIO_REGION = 'us-east-1'
MINIO_SIGNATURE_VERSION = 's3v4'

CERT_SECRET_NAME = "ca-cert-secret"

try:
    configuration = config.load_kube_config()
except Exception:
    configuration = config.load_incluster_config()

api_instance = client.CoreV1Api(client.ApiClient(configuration))

minio = boto3.resource('s3',
                       endpoint_url=MINIO_ENDPOINT_ADDR,
                       aws_access_key_id=MINIO_ACCESS_KEY_ID,
                       aws_secret_access_key=MINIO_SECRET_ACCESS_KEY,
                       config=Config(signature_version=MINIO_SIGNATURE_VERSION),
                       region_name=MINIO_REGION)
