import re
import ipaddress
from functools import lru_cache
from kubernetes import config, client
from kubernetes.client.rest import ApiException

from management_api.utils.errors_handling import InvalidParamException, KubernetesGetException
from management_api.utils.logger import get_logger
from management_api.config import ING_NAME, ING_NAMESPACE, ValidityMessage

logger = get_logger(__name__)


def validate_quota(quota):
    int_keys = ['maxEndpoints']
    alpha_keys = ['requests.memory', 'limits.memory', 'requests.cpu', 'limits.cpu']
    regex_k8s = '^([+]?[0-9.]+)([eEinumkKMGTP]*[+]?[0-9]*)$'

    test_quota = dict(quota)
    for key, value in quota.items():
        if key in int_keys:
            if not value.isdigit() > 0:
                raise InvalidParamException('<int param>', 'Invalid value {} of {} field'.
                                            format(value, key), ValidityMessage.QUOTA_INT_VALUES)
            test_quota.pop(key)
        if key in alpha_keys:
            if not re.match(regex_k8s, value):
                raise InvalidParamException('<alpha_param>', 'Invalid value {} of {} field'.
                                            format(value, key), ValidityMessage.QUOTA_ALPHA_VALUES)
            test_quota.pop(key)

    if test_quota:
        logger.info("There are some redundant values provided that won't be used:")
        for key, value in test_quota.items():
            logger.info(key + ": " + value)
            quota.pop(key)
    logger.info('Resource quota {} is valid'.format(quota))
    return True


def transform_quota(quota):
    transformed = {}
    for k, v in quota.items():
        keys = k.split('.')
        if len(keys) == 1:
            continue
        transformed.setdefault(keys[0], {})[keys[1]] = v
    return transformed


def read_resource_quota(api_instance: client, name, namespace):
    try:
        tenant_quota = api_instance.read_namespaced_resource_quota(
            name=name, namespace=namespace)
    except ApiException as apiException:
        raise KubernetesGetException('resource quota', apiException)
    return tenant_quota


def validate_quota_compliance(api_instance: client, namespace, endpoint_quota):
    tenant_quota = read_resource_quota(api_instance, name=namespace, namespace=namespace)
    tenant_quota = tenant_quota.spec.hard
    if tenant_quota is not None:
        if endpoint_quota == {}:
            raise InvalidParamException("endpoint_quota",
                                        "No endpoint quota provided.",
                                        'There\'s resource quota specified in {} tenant: {} '
                                        'Please fill resource field with given keys in your request'
                                        .format(namespace, tenant_quota))
        if not tenant_quota.keys() == endpoint_quota.keys():
            missing_pairs = {k: v for k, v in tenant_quota.items()
                             if k not in endpoint_quota.keys()}
            if missing_pairs:
                raise InvalidParamException("endpoint_quota",
                                            "Missing endpoint quota values.",
                                            'You need to provide: {}'
                                            .format(missing_pairs))
    return True


def get_ingress_external_ip(api_instance: client):
    api_response = api_instance.read_namespaced_service(ING_NAME, ING_NAMESPACE)
    ip = api_response.status.load_balancer.ingress[0].ip
    port = api_response.spec.ports[-1].port
    ipaddress.ip_address(ip)
    port = int(port)
    return ip, port


@lru_cache(maxsize=None)
def get_k8s_configuration():
    try:
        configuration = config.load_kube_config()
    except Exception:
        configuration = config.load_incluster_config()
    return configuration


@lru_cache(maxsize=None)
def get_k8s_api_client():
    api_instance = client.CoreV1Api(client.ApiClient(get_k8s_configuration()))
    return api_instance


@lru_cache(maxsize=None)
def get_k8s_api_custom_client():
    custom_obj_api_instance = client.CustomObjectsApi(client.ApiClient(get_k8s_configuration()))
    return custom_obj_api_instance


@lru_cache(maxsize=None)
def get_k8s_rbac_api_client():
    rbac_api_instance = client.RbacAuthorizationV1Api(client.ApiClient(get_k8s_configuration()))
    return rbac_api_instance
