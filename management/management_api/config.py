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
SIGNATURE_VERSION = 's3v4'

CERT_SECRET_NAME = 'ca-cert-secret'
PORTABLE_SECRETS_PATHS = ['default/minio-access-info', 'default/tls-secret']

PLATFORM_DOMAIN = os.environ['PLATFORM_DOMAIN']

# CRD DEFINITIONS:
CRD_GROUP = 'intel.com' # str | The custom resource's group name
CRD_VERSION = 'v1' # str | The custom resource's version
CRD_PLURAL = 'servers' # str | The custom resource's plural name. For TPRs this would be lowercase plural kind.
CRD_API_VERSION = 'intel.com/v1'
CRD_KIND = 'Server'

ING_NAME = 'ingress-nginx'
ING_NAMESPACE = 'ingress-nginx'

try:
    configuration = config.load_kube_config()
except Exception:
    configuration = config.load_incluster_config()

api_instance = client.CoreV1Api(client.ApiClient(configuration))
custom_obj_api_instance = client.CustomObjectsApi(client.ApiClient(configuration))

minio_client = boto3.client('s3',
                            endpoint_url=MINIO_ENDPOINT_ADDR,
                            aws_access_key_id=MINIO_ACCESS_KEY_ID,
                            aws_secret_access_key=MINIO_SECRET_ACCESS_KEY,
                            config=Config(
                                    signature_version=SIGNATURE_VERSION),
                            region_name=MINIO_REGION)

minio_resource = boto3.resource('s3',
                                endpoint_url=MINIO_ENDPOINT_ADDR,
                                aws_access_key_id=MINIO_ACCESS_KEY_ID,
                                aws_secret_access_key=MINIO_SECRET_ACCESS_KEY,
                                config=Config(
                                        signature_version=SIGNATURE_VERSION),
                                region_name=MINIO_REGION)
