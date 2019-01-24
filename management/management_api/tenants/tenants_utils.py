#
# Copyright (c) 2018-2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import falcon
from botocore.exceptions import ClientError
from kubernetes import client as k8s_client
from kubernetes.client.rest import ApiException
from tenacity import retry, stop_after_attempt, wait_fixed
from management_api.config import CERT_SECRET_NAME, PORTABLE_SECRETS_PATHS, \
    minio_client, minio_resource, RESOURCE_DOES_NOT_EXIST, K8S_FORBIDDEN, \
    NAMESPACE_BEING_DELETED, NO_SUCH_BUCKET_EXCEPTION, TERMINATION_IN_PROGRESS, PLATFORM_ADMIN_LABEL
from management_api.utils.cert import validate_cert
from management_api.utils.errors_handling import TenantAlreadyExistsException, MinioCallException, \
    TenantDoesNotExistException, KubernetesCreateException, KubernetesDeleteException, \
    KubernetesGetException, KubernetesForbiddenException
from management_api.utils.kubernetes_resources import get_k8s_api_client, get_k8s_rbac_api_client
from management_api.utils.logger import get_logger

logger = get_logger(__name__)


def create_tenant(parameters, id_token):
    name = parameters['name']
    cert = parameters['cert']
    scope = parameters['scope']
    quota = parameters['quota']

    logger.info('Creating new tenant: {}'
                .format(name, cert, scope, quota))

    validate_cert(cert)

    if tenant_exists(name, id_token):
        raise TenantAlreadyExistsException(name)

    try:
        create_namespace(name, quota, id_token)
        propagate_portable_secrets(target_namespace=name, id_token=id_token)
        create_bucket(name)
        create_secret(name, cert, id_token=id_token)
        create_resource_quota(name, quota, id_token=id_token)
        create_role(name, id_token=id_token)
        create_rolebinding(name, scope, id_token=id_token)
    except falcon.HTTPError:
        delete_namespace(name, id_token=id_token)
        delete_bucket(name, id_token=id_token)
        raise

    logger.info('Tenant {} created'.format(name))
    return name


def create_namespace(name, quota, id_token):
    annotations = None
    if 'maxEndpoints' in quota:
        annotations = {'maxEndpoints': str(quota.pop('maxEndpoints'))}
    name_object = k8s_client.V1ObjectMeta(name=name, annotations=annotations,
                                          labels={'created_by': PLATFORM_ADMIN_LABEL})
    namespace = k8s_client.V1Namespace(metadata=name_object)
    api_instance = get_k8s_api_client(id_token=id_token)
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


def create_secret(name, cert, id_token):
    cert_secret_metadata = k8s_client.V1ObjectMeta(name=CERT_SECRET_NAME)
    cert_secret_data = {"ca.crt": cert}
    cert_secret = k8s_client.V1Secret(api_version="v1", data=cert_secret_data,
                                      kind="Secret", metadata=cert_secret_metadata,
                                      type="Opaque")
    api_instance = get_k8s_api_client(id_token)
    try:
        response = api_instance.create_namespaced_secret(namespace=name,
                                                         body=cert_secret)
    except ApiException as apiException:
        raise KubernetesCreateException('secret', apiException)

    logger.info('Secret {} created'.format(CERT_SECRET_NAME))
    return response


def create_resource_quota(name, quota, id_token):
    name_object = k8s_client.V1ObjectMeta(name=name)
    resource_quota_spec = k8s_client.V1ResourceQuotaSpec(hard=quota)
    body = k8s_client.V1ResourceQuota(spec=resource_quota_spec, metadata=name_object)
    api_instance = get_k8s_api_client(id_token)
    try:
        response = api_instance.create_namespaced_resource_quota(name, body)
    except ApiException as apiException:
        raise KubernetesCreateException('resource_quota', apiException)

    logger.info("Resource quota {} created".format(quota))
    return response


@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
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


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def delete_namespace(name, id_token):
    body = k8s_client.V1DeleteOptions()
    response = 'Namespace {} does not exist'.format(name)
    api_instance = get_k8s_api_client(id_token)
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


def delete_tenant(parameters, id_token):
    name = parameters['name']
    logger.info('Deleting tenant: {}'.format(name))
    if tenant_exists(name, id_token=id_token):
        delete_bucket(name)
        delete_namespace(name, id_token)
        logger.info('Tenant {} deleted'.format(name))
    else:
        raise TenantDoesNotExistException(name)
    return name


def propagate_secret(source_secret_path, target_namespace, id_token):
    source_secret_namespace, source_secret_name = source_secret_path.split('/')
    api_instance = get_k8s_api_client(id_token)
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


def propagate_portable_secrets(target_namespace, id_token):
    for portable_secret_path in PORTABLE_SECRETS_PATHS:
            propagate_secret(portable_secret_path, target_namespace, id_token=id_token)
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


def is_namespace_available(namespace, id_token):
    api_instance = get_k8s_api_client(id_token)
    try:
        response = api_instance.read_namespace_status(namespace)
    except ApiException as apiException:
        if apiException.status == RESOURCE_DOES_NOT_EXIST:
            return False
        if apiException.status == K8S_FORBIDDEN:
            raise KubernetesForbiddenException('forbidden', apiException)
        raise KubernetesGetException('namespace status', apiException)
    if response and response.status.phase == TERMINATION_IN_PROGRESS:
        return False
    return True


def tenant_exists(tenant_name, id_token):
    result = does_bucket_exist(tenant_name) and is_namespace_available(tenant_name, id_token)
    logger.info("Tenant already exists: " + str(result))
    return result


def create_role(name, id_token):
    api_version = 'rbac.authorization.k8s.io/v1'
    meta = k8s_client.V1ObjectMeta(name=name, namespace=name)
    service_rules = k8s_client.V1PolicyRule(api_groups=[""], resources=["services"],
                                            verbs=["create", "list", "get", "delete"])
    quotas_rules = k8s_client.V1PolicyRule(api_groups=[""], resources=["resourcequotas"],
                                           verbs=["create", "list", "get", "delete"])
    ingress_rules = k8s_client.V1PolicyRule(api_groups=[""], resources=["ingresses"],
                                            verbs=["create", "list", "get", "delete"])
    deployment_rules = k8s_client.V1PolicyRule(api_groups=[""], resources=["deployments"],
                                               verbs=["create", "list", "get", "delete"])
    server_rules = k8s_client.V1PolicyRule(api_groups=["ai.intel.com"],
                                           resources=["inference-endpoints"],
                                           verbs=["create", "get", "delete", "patch"])
    namespace_rules = k8s_client.V1PolicyRule(api_groups=[""], resources=["namespaces"],
                                              verbs=["get", "list", "watch"])
    ns_status_rules = k8s_client.V1PolicyRule(api_groups=[""], resources=["namespaces/status"],
                                              verbs=["get", "list", "watch"])
    list_pods_rule = k8s_client.V1PolicyRule(api_groups=[""], resources=["pods"],
                                             verbs=["list"])
    deployment_apps_rule = k8s_client.V1PolicyRule(api_groups=["apps"],
                                                   resources=["deployments",
                                                              "deployments/status"],
                                                   verbs=["list", "get"])

    role = k8s_client.V1Role(api_version=api_version, metadata=meta,
                             rules=[service_rules, ingress_rules, deployment_rules,
                                    server_rules, namespace_rules, ns_status_rules,
                                    quotas_rules, list_pods_rule, deployment_apps_rule])

    rbac_api_instance = get_k8s_rbac_api_client(id_token)
    try:
        response = rbac_api_instance.create_namespaced_role(name, role)
    except ApiException as apiException:
        raise KubernetesCreateException('role', apiException)

    logger.info("Role {} created".format(name))
    return response


def create_rolebinding(name, scope_name, id_token):
    api_version = 'rbac.authorization.k8s.io'
    scope = scope_name
    subject = k8s_client.V1Subject(kind='Group', name=scope, namespace=name)
    role_ref = k8s_client.V1RoleRef(api_group=api_version, kind='Role', name=name)
    meta = k8s_client.V1ObjectMeta(name=name, namespace=name)
    rolebinding = k8s_client.V1RoleBinding(metadata=meta, role_ref=role_ref, subjects=[subject])
    rbac_api_instance = get_k8s_rbac_api_client(id_token)

    try:
        response = rbac_api_instance.create_namespaced_role_binding(name, rolebinding)
    except ApiException as apiException:
        KubernetesCreateException('rolebinding', apiException)

    logger.info("Rolebinding {} created".format(name))
    return response


def list_tenants(id_token):
    tenants = []
    api_instance = get_k8s_api_client(id_token)
    label = f'created_by = {PLATFORM_ADMIN_LABEL}'
    namespaces = {}
    try:
        namespaces = api_instance.list_namespace(label_selector=label)
    except ApiException as apiException:
        KubernetesGetException('namespaces', apiException)
    for item in namespaces.to_dict()['items']:
        if item['status']['phase'] != TERMINATION_IN_PROGRESS:
            tenants.append(item['metadata']['name'])
    if not tenants:
        message = "There are no tenants present on platform\n"
        logger.info(message)
        return message
    message = f"Tenants present on platform: {tenants}\n"
    logger.info(message)
    return message
