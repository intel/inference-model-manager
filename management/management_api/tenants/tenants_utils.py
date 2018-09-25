import re

import falcon
from botocore.exceptions import ClientError
from kubernetes import client
from kubernetes.client.rest import ApiException
from retrying import retry

from management_api.config import CERT_SECRET_NAME, PORTABLE_SECRETS_PATHS, \
    minio_client, minio_resource, RESOURCE_DOES_NOT_EXIST, \
    NAMESPACE_BEING_DELETED, NO_SUCH_BUCKET_EXCEPTION, TERMINATION_IN_PROGRESS, ValidityMessage
from management_api.utils.cert import validate_cert
from management_api.utils.errors_handling import TenantAlreadyExistsException, MinioCallException, \
    TenantDoesNotExistException, InvalidParamException, KubernetesCreateException, \
    KubernetesDeleteException, KubernetesGetException
from management_api.utils.kubernetes_resources import validate_quota, get_k8s_api_client, \
    get_k8s_rbac_api_client
from management_api.utils.logger import get_logger

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

    if tenant_exists(name):
        raise TenantAlreadyExistsException(name)

    try:
        create_namespace(name, quota)
        propagate_portable_secrets(target_namespace=name)
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
        raise InvalidParamException('name', "Tenant name '{}' has wrong format"
                                    .format(name), ValidityMessage.TENANT_NAME)
    if len(name) < 3:
        raise InvalidParamException('name', "Tenant name '{}' is too short"
                                    .format(name), ValidityMessage.TENANT_NAME)
    if len(name) > 63:
        raise InvalidParamException('name', "Tenant name '{}'is too long"
                                    .format(name), ValidityMessage.TENANT_NAME)


def create_namespace(name, quota):
    if 'maxEndpoints' in quota:
        name_object = client.V1ObjectMeta(name=name,
                                          annotations={'maxEndpoints': quota.pop('maxEndpoints')})
    else:
        name_object = client.V1ObjectMeta(name=name)
    namespace = client.V1Namespace(metadata=name_object)
    api_instance = get_k8s_api_client()
    try:
        response = api_instance.create_namespace(namespace)
    except ApiException as apiException:
        raise KubernetesCreateException('namespace', apiException)

    logger.info("Namespace {} created".format(name))
    return response


def create_bucket(name):
    try:
        response = minio_client.create_bucket(Bucket=name)
    except ClientError as clientError:
        raise MinioCallException('An error occurred during bucket creation: {}'.format(clientError))

    logger.info('Bucket created: {}'.format(response))
    return response


def create_secret(name, cert):
    cert_secret_metadata = client.V1ObjectMeta(name=CERT_SECRET_NAME)
    cert_secret_data = {"ca.crt": cert}
    cert_secret = client.V1Secret(api_version="v1", data=cert_secret_data,
                                  kind="Secret", metadata=cert_secret_metadata,
                                  type="Opaque")
    api_instance = get_k8s_api_client()
    try:
        response = api_instance.create_namespaced_secret(namespace=name,
                                                         body=cert_secret)
    except ApiException as apiException:
        raise KubernetesCreateException('secret', apiException)

    logger.info('Secret {} created'.format(CERT_SECRET_NAME))
    return response


def create_resource_quota(name, quota):
    name_object = client.V1ObjectMeta(name=name)
    resource_quota_spec = client.V1ResourceQuotaSpec(hard=quota)
    body = client.V1ResourceQuota(spec=resource_quota_spec, metadata=name_object)
    api_instance = get_k8s_api_client()
    try:
        response = api_instance.create_namespaced_resource_quota(name, body)
    except ApiException as apiException:
        raise KubernetesCreateException('resource_quota', apiException)

    logger.info("Resource quota {} created".format(quota))
    return response


@retry(stop_max_attempt_number=5, wait_fixed=2000)
def delete_bucket(name):
    response = 'Bucket {} does not exist'.format(name)
    existed = True
    try:
        bucket = minio_resource.Bucket(name)
        bucket.objects.all().delete()
        response = bucket.delete()
    except ClientError as clientError:
        if clientError.response['Error']['Code'] != NO_SUCH_BUCKET_EXCEPTION:
            raise MinioCallException("A error occurred during bucket deletion: {}"
                                     .format(clientError))
        existed = False
    if existed:
        logger.info('Bucket {} deleted'.format(name))
    else:
        logger.info('Bucket {} does not exist'.format(name))
    return response


@retry(stop_max_attempt_number=5, wait_fixed=2000)
def delete_namespace(name):
    body = client.V1DeleteOptions()
    response = 'Namespace {} does not exist'.format(name)
    api_instance = get_k8s_api_client()
    existed = True
    try:
        response = api_instance.delete_namespace(name, body)
    except ApiException as apiException:
        if apiException.status != RESOURCE_DOES_NOT_EXIST and \
                apiException.status != NAMESPACE_BEING_DELETED:
            raise KubernetesDeleteException('namespace', apiException)
        existed = False
    if existed:
        logger.info('Namespace {} deleted'.format(name))
    else:
        logger.info('Namespace {} does not exist'.format(name))

    return response


def delete_tenant(parameters):
    name = parameters['name']
    logger.info('Deleting tenant: {}'.format(name))
    if tenant_exists(name):
        delete_bucket(name)
        delete_namespace(name)
        logger.info('Tenant {} deleted'.format(name))
    else:
        raise TenantDoesNotExistException(name)


def propagate_secret(source_secret_path, target_namespace):
    source_secret_namespace, source_secret_name = source_secret_path.split('/')
    api_instance = get_k8s_api_client()
    try:
        source_secret = api_instance.read_namespaced_secret(
            source_secret_name, source_secret_namespace)
    except ApiException as apiException:
        raise KubernetesGetException('secret', apiException)

    source_secret.metadata.namespace = target_namespace
    source_secret.metadata.resource_version = None

    try:
        api_instance.create_namespaced_secret(namespace=target_namespace,
                                              body=source_secret)
    except ApiException as apiException:
        raise KubernetesCreateException('secret', apiException)


def propagate_portable_secrets(target_namespace):
    for portable_secret_path in PORTABLE_SECRETS_PATHS:
            propagate_secret(portable_secret_path, target_namespace)
    logger.info('Portable secrets copied from default to {}'.format(target_namespace))


def does_bucket_exist(bucket_name):
    try:
        minio_client.list_objects_v2(Bucket=bucket_name)
    except ClientError as clientError:
        error_code = clientError.response['Error']['Code']
        if error_code == NO_SUCH_BUCKET_EXCEPTION:
            return False
        raise MinioCallException("Error accessing bucket: {}".format(clientError))
    return True


def is_namespace_available(namespace):
    response = None
    api_instance = get_k8s_api_client()
    try:
        response = api_instance.read_namespace_status(namespace)
    except ApiException as apiException:
        if apiException.status == RESOURCE_DOES_NOT_EXIST:
            return False
        raise KubernetesGetException('namespace status', apiException)
    if response and response.status.phase == TERMINATION_IN_PROGRESS:
        return False
    return True


def tenant_exists(tenant_name):
    result = does_bucket_exist(tenant_name) and is_namespace_available(tenant_name)
    logger.info("Tenant already exists: " + str(result))
    return result


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
    rbac_api_instance = get_k8s_rbac_api_client()
    try:
        response = rbac_api_instance.create_namespaced_role(name, role)
    except ApiException as apiException:
        raise KubernetesCreateException('role', apiException)

    logger.info("Role {} created".format(name))
    return response


def create_rolebinding(name, scope_name):
    api_version = 'rbac.authorization.k8s.io'
    scope = 'oidc:/' + scope_name
    subject = client.V1Subject(kind='Group', name=scope, namespace=name)
    role_ref = client.V1RoleRef(api_group=api_version, kind='Role', name=name)
    meta = client.V1ObjectMeta(name=name, namespace=name)
    rolebinding = client.V1RoleBinding(metadata=meta, role_ref=role_ref, subjects=[subject])
    rbac_api_instance = get_k8s_rbac_api_client()

    try:
        response = rbac_api_instance.create_namespaced_role_binding(name, rolebinding)
    except ApiException as apiException:
        KubernetesCreateException('rolebinding', apiException)

    logger.info("Rolebinding {} created".format(name))
    return response
