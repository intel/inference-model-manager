import falcon
import re

from botocore.exceptions import ClientError
from kubernetes import client
from kubernetes.client.rest import ApiException
from retrying import retry

from management_api.config import CERT_SECRET_NAME, PORTABLE_SECRETS_PATHS,\
    api_instance, rbac_api_instance, minio_client, minio_resource, \
    RESOURCE_DOES_NOT_EXIST, NAMESPACE_BEING_DELETED, NO_SUCH_BUCKET_EXCEPTION
from management_api.utils.logger import get_logger
from management_api.utils.cert import validate_cert
from management_api.utils.kubernetes_resources import validate_quota


logger = get_logger(__name__)


def create_tenant(parameters):
    name = parameters['name']
    cert = parameters['cert']
    scope = parameters['scope']
    quota = parameters['quota']

    logger.info('Creating new tenant: {}'
                .format(name, cert, scope, quota))

    validate_cert(cert)
    validate_tenant_name(name)
    validate_quota(quota)
    try:
        create_namespace(name, quota)
        portable_secrets_propagation(target_namespace=name)
        create_bucket(name)
        create_secret(name, cert)
        create_resource_quota(name, quota)
        create_role(name)
        create_rolebinding(name, scope)
    except falcon.HTTPError:
        delete_namespace(name)
        delete_bucket(name)
        raise
    logger.info('Tenant {} created'.format(name))


def validate_tenant_name(name):
    regex_k8s = '^[a-z0-9]([-a-z0-9]*[a-z0-9])?$'
    if not re.match(regex_k8s, name):
        logger.error('Tenant name {} is not valid: must consist of '
                     'lower case alphanumeric characters or \'-\', '
                     'and must start and end with an alphanumeric character '
                     '(e.g. \'my-name\', or \'123-abc\')'.format(name))
        raise falcon.HTTPBadRequest('Tenant name {} is not valid: must consist of '
                                    'lower case alphanumeric characters or \'-\', '
                                    'and must start and end with an alphanumeric character '
                                    '(e.g. \'my-name\', or \'123-abc\')'.format(name))
    if len(name) < 3:
        logger.error('Tenant name {} is not valid: too short'.format(name))
        raise falcon.HTTPBadRequest('Tenant name {} is not valid: '
                                    'too short. Provide a tenant name '
                                    'which is at least 3 character long'.format(name))
    if len(name) > 63:
        logger.error('Tenant name {} is not valid: too long'.format(name))
        raise falcon.HTTPBadRequest('Tenant name {} is not valid: '
                                    'too long. Provide a tenant name '
                                    'which is max 63 character long'.format(name))


def create_namespace(name, quota):
    if 'maxEndpoints' in quota:
        name_object = client.V1ObjectMeta(name=name,
                                          annotations={'maxEndpoints': quota.pop('maxEndpoints')})
    else:
        name_object = client.V1ObjectMeta(name=name)
    namespace = client.V1Namespace(metadata=name_object)
    try:
        response = api_instance.create_namespace(namespace)
    except ApiException as apiException:
        logger.error('Did not create namespace: {}'.format(apiException))
        raise falcon.HTTPBadRequest('Did not create namespace: {}'.format(apiException))
    except Exception as e:
        logger.error('An error occurred during namespace creation: {}'
                     .format(e))
        raise falcon.HTTPBadRequest('An error occurred during namespace '
                                    'creation: {}'.format(e))
    logger.info("Namespace {} created".format(name))
    return response


def create_bucket(name):
    try:
        response = minio_client.create_bucket(Bucket=name)
    except ClientError as clientError:
        logger.error('ClientError occurred: {}'.format(clientError))
        raise falcon.HTTPBadRequest('ClientError occurred: {}'.format(clientError))
    except Exception as e:
        logger.error('An error occurred during bucket creation: {}'.format(e))
        raise falcon.HTTPBadRequest('An error occurred during bucket '
                                    'creation: {}'.format(e))
    logger.info('Bucket created: {}'.format(response))
    return response


def create_secret(name, cert):
    cert_secret_metadata = client.V1ObjectMeta(name=CERT_SECRET_NAME)
    cert_secret_data = {"ca.crt": cert}
    cert_secret = client.V1Secret(api_version="v1", data=cert_secret_data,
                                  kind="Secret", metadata=cert_secret_metadata,
                                  type="Opaque")
    try:
        response = api_instance.create_namespaced_secret(namespace=name,
                                                         body=cert_secret)
    except ApiException as apiException:
        logger.error('Did not create secret: {}'.format(apiException))
        raise falcon.HTTPBadRequest('Did not create secret: {}'
                                    .format(apiException))
    except Exception as e:
        logger.error('An error occurred during secret creation:'
                     ' {}'.format(e))
        raise falcon.HTTPBadRequest('An error occurred during secret '
                                    'creation: {}'.format(e))
    logger.info('Secret {} created'.format(CERT_SECRET_NAME))
    return response


def create_resource_quota(name, quota):
    name_object = client.V1ObjectMeta(name=name)
    resource_quota_spec = client.V1ResourceQuotaSpec(hard=quota)
    body = client.V1ResourceQuota(spec=resource_quota_spec, metadata=name_object)

    try:
        response = api_instance.create_namespaced_resource_quota(name, body)
        logger.info("Resource quota {} created".format(quota))
    except ApiException as apiException:
        logger.error("Resource quota not created: {}".format(apiException))
        raise falcon.HTTPBadRequest('An error occurred during resource quota creation: {}'.format(
                apiException))
    except Exception as e:
        logger.error('Error occurred: {}'.format(e))
        raise falcon.HTTPBadRequest('Error occurred: {}'.format(e))
    return response


@retry(stop_max_attempt_number=5, wait_fixed=2000)
def delete_bucket(name):
    response = 'Bucket {} does not exist'.format(name)
    try:
        bucket = minio_resource.Bucket(name)
        bucket.objects.all().delete()
        response = bucket.delete()
    except ClientError as clientError:
        logger.error('Error occurred during bucket deletion: {}'.
                     format(clientError))
        if clientError.response['Error']['Code'] != NO_SUCH_BUCKET_EXCEPTION:
            raise falcon.HTTPBadRequest('Error occurred during bucket '
                                        'deletion: {}'.format(clientError))
    except Exception as e:
        logger.error('Unexpected error occurred during bucket deletion: {}'.format(e))
        raise falcon.HTTPBadRequest('Unexpected error occurred during bucket deletion: {}'
                                    .format(e))

    logger.info('Bucket {} deleted'.format(name))
    return response


@retry(stop_max_attempt_number=5, wait_fixed=2000)
def delete_namespace(name):
    body = client.V1DeleteOptions()
    response = 'Namespace {} does not exist'.format(name)
    try:
        response = api_instance.delete_namespace(name, body)
    except ApiException as apiException:
        if apiException.status != RESOURCE_DOES_NOT_EXIST and \
                        apiException.status != NAMESPACE_BEING_DELETED:
            logger.error('Error occurred during namespace deletion: {}'.format(apiException.status))
            raise falcon.HTTPBadRequest('Error occurred during namespace deletion: {}'
                                        .format(apiException))
    except Exception as e:
        logger.error('Error occurred during namespace deletion: {}'.format(e.status))
        raise falcon.HTTPBadRequest('Error occurred during namespace deletion: {}'
                                    .format(e))
    logger.info('Namespace {} deleted'.format(name))
    return response


def delete_tenant(parameters):
    name = parameters['name']
    logger.info('Deleting tenant: {}'.format(name))
    delete_bucket(name)
    delete_namespace(name)
    logger.info('Tenant {} deleted'.format(name))


def propagate_secret(source_secret_path, target_namespace):
    source_secret_namespace, source_secret_name = source_secret_path.split('/')
    try:
        source_secret = api_instance.read_namespaced_secret(
            source_secret_name, source_secret_namespace)
    except ApiException as apiException:
        logger.error('Error reading secret to propagate: {}'.format(
            apiException))
        raise falcon.HTTPBadRequest(
            'Error reading secret to propagate:'.format(apiException))

    source_secret.metadata.namespace = target_namespace
    source_secret.metadata.resource_version = None

    try:
        api_instance.create_namespaced_secret(namespace=target_namespace,
                                              body=source_secret)
    except ApiException as apiException:
        logger.error('Error creating propagated secret in new ''namespace: {}'
                     .format(apiException))
        raise falcon.HTTPBadRequest(
            'Error creating propagated secret in new namespace: {}'.format(apiException))


def portable_secrets_propagation(target_namespace):
    for portable_secret_path in PORTABLE_SECRETS_PATHS:
        try:
            propagate_secret(portable_secret_path, target_namespace)
        except Exception:
            raise falcon.HTTPBadRequest('Error occurred on secret propagation')
    logger.info('Portable secrets copied from default to {}'.format(target_namespace))


def create_role(name):
    api_version = 'rbac.authorization.k8s.io/v1'
    meta = client.V1ObjectMeta(name=name, namespace=name)
    service_rules = client.V1PolicyRule(api_groups=[""], resources=["services"], 
                                        verbs=["create", "list", "get", "delete"])
    ingress_rules = client.V1PolicyRule(api_groups=[""], resources=["ingresses"], 
                                        verbs=["create", "list", "get", "delete"])
    deployment_rules = client.V1PolicyRule(api_groups=[""], resources=["deployments"], 
                                        verbs=["create", "list", "get", "delete"])
    server_rules = client.V1PolicyRule(api_groups=["intel.com"], resources=["servers"], 
                                        verbs=["create", "get", "delete", "patch"])
    role = client.V1Role(api_version=api_version, metadata=meta, 
                  rules=[service_rules, ingress_rules, deployment_rules, server_rules])

    try:
        response = rbac_api_instance.create_namespaced_role(name, role)
    except ApiException as apiException:
        logger.error('Did not create role: {}'.format(apiException))
        raise falcon.HTTPBadRequest('Did not create role: {}'.format(apiException))
    except Exception as e:
        logger.error('An error occurred during role creation: {}'
                     .format(e))
        raise falcon.HTTPBadRequest('An error occurred during role '
                                    'creation: {}'.format(e))
    
    logger.info("Role {} created".format(name))
    return response


def create_rolebinding(name, scope_name):
    api_version = 'rbac.authorization.k8s.io' 
    scope = 'oidc:/' + scope_name
    subject = client.V1Subject(kind='Group', name=scope, namespace=name)
    role_ref = client.V1RoleRef(api_group=api_version, kind='Role', name=name)
    meta = client.V1ObjectMeta(name=name, namespace=name)
    rolebinding = client.V1RoleBinding(metadata=meta, role_ref=role_ref, subjects=[subject])
    
    try:
        response = rbac_api_instance.create_namespaced_role_binding(name, rolebinding)
    except ApiException as apiException:
        logger.error('Did not create rolebinding: {}'.format(apiException))
        raise falcon.HTTPBadRequest('Did not create rolebinding: {}'.format(apiException))
    except Exception as e:
        logger.error('An error occured during rolebinding creation: {}'.format(e))
        raise falcon.HTTPBadRequest('An error occured during rolebinding creation: {}'.format(e))
    
    logger.info("Rolebinding {} created".format(name))
    return response 

