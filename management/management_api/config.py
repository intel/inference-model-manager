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
PLATFORM_ADMIN = os.getenv('PLATFORM_ADMIN', 'platform_admin')


# AUTH CONTROLLER DEFINITIONS:
class AuthParameters:
    REDIRECT_URL = os.getenv('AUTH_REDIRECT_URL', 'http://127.0.0.1:5555/callback')
    CLIENT_ID = os.getenv('AUTH_CLIENT_ID', 'example-app')
    RESPONSE_TYPE = 'code'
    SCOPE = 'groups openid email'
    CLIENT_SECRET = os.getenv('AUTH_CLIENT_SECRET', 'ZXhhbXBsZS1hcHAtc2VjcmV0')
    TOKEN_PATH = os.getenv('AUTH_TOKEN_PATH', '/dex/token')
    AUTH_PATH = os.getenv('AUTH_TOKEN_PATH', '/dex/auth')
    ADMIN_SCOPE = os.getenv('ADMIN_SCOPE', 'admin')
    SYSTEM_NAMESPACE = os.getenv('SYSTEM_NAMESPACE', 'default')


# CRD DEFINITIONS:
CRD_GROUP = 'aipg.intel.com'
CRD_VERSION = 'v1'
CRD_PLURAL = 'servers'
CRD_API_VERSION = 'aipg.intel.com/v1'
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


# To edit this object please first use deep copy
DELETE_BODY = client.V1DeleteOptions()

# -------------------------------------------
RESOURCE_DOES_NOT_EXIST = 404
NAMESPACE_BEING_DELETED = 409
TERMINATION_IN_PROGRESS = 'Terminating'
NO_SUCH_BUCKET_EXCEPTION = 'NoSuchBucket'
REPLICA_FAILURE = 'ReplicaFailure'


class ValidityMessage:
    CERTIFICATE = "Provided certificate does not look like valid certificate. " \
                  "Please check if it's correctly Base64 encoded and not corrupted " \
                  "in any way."
