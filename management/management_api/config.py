import boto3
import os
from botocore.client import Config
from kubernetes import client

HOSTNAME = os.getenv('HOSTNAME', 'localhost')
PORT = int(os.getenv('PORT', 5000))
MINIO_ACCESS_KEY_ID = os.getenv('MINIO_ACCESS_KEY_ID', 'default')
MINIO_SECRET_ACCESS_KEY = os.getenv('MINIO_SECRET_ACCESS_KEY', 'default')
MINIO_ENDPOINT_ADDR = os.getenv('MINIO_ENDPOINT_ADDR', 'http://127.0.0.1:9000')

MINIO_REGION = 'us-east-1'
SIGNATURE_VERSION = 's3v4'

CERT_SECRET_NAME = 'ca-cert-secret'
PORTABLE_SECRETS_PATHS = ['default/minio-access-info', 'default/tls-secret']

PLATFORM_DOMAIN = os.getenv('PLATFORM_DOMAIN', 'default')

# CRD DEFINITIONS:
CRD_GROUP = 'intel.com'
CRD_VERSION = 'v1'
CRD_PLURAL = 'servers'
CRD_API_VERSION = 'intel.com/v1'
CRD_KIND = 'Server'

ING_NAME = 'ingress-nginx'
ING_NAMESPACE = 'ingress-nginx'

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
# -----------------------------------------
# ENDPOINT RELATED CONSTANTS


class RequiredParameters:

    CREATE_ENDPOINT = ['modelName', 'modelVersion', 'endpointName', 'subjectName']
    UPDATE_ENDPOINT = ['modelName', 'modelVersion']
    SCALE_ENDPOINT = ['replicas']
    DELETE_ENDPOINT = ['endpointName']
    CREATE_TENANT = ['name', 'cert', 'scope', 'quota']
    DELETE_TENANT = ['name']
    MULTIPART_START = ['modelName', 'modelVersion']


# To edit this object please first use deep copy
DELETE_BODY = client.V1DeleteOptions()

SUBJECT_NAME_RE = '^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|' \
                  '[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$'

# -------------------------------------------
RESOURCE_DOES_NOT_EXIST = 404
NAMESPACE_BEING_DELETED = 409
TERMINATION_IN_PROGRESS = 'Terminating'
NO_SUCH_BUCKET_EXCEPTION = 'NoSuchBucket'


class ValidityMessage:
    SUBJECT_NAME = "Subject name must contain alphanumeric characters, " \
                   "'-' and '.'(provided it's not last character). " \
                   "It shall follow regex: " + SUBJECT_NAME_RE + \
                   "Examples: example.com, another-example.com, " \
                   "one-more-example.org.com"
    ENDPOINT_INT_VALUES = "For modelVersion and replicas fields, please provide " \
                          "integers greater than 0"
    TENANT_NAME = "Tenant name must consist of at least 3 and maximum 63 " \
                  "lower case alphanumeric characters or '-', and must " \
                  "start and end with an alphanumeric character " \
                  "(e.g. 'my-name', or '123-abc')"

    QUOTA_ALPHA_VALUES = "Please provide value that matches Kubernetes convention. " \
                         "Some example values: '1Gi', '200Mi', '300m'"
    QUOTA_INT_VALUES = "Please provide integer greater than or equal to 0"

    CERTIFICATE = "Provided certificate does not look like valid certificate. " \
                  "Please check if it's correctly Base64 encoded and not corrupted " \
                  "in any way."
