import re
import falcon
import ipaddress
from functools import lru_cache
from kubernetes import config, client

from management_api.utils.logger import get_logger
from management_api.config import ING_NAME, ING_NAMESPACE

logger = get_logger(__name__)


def validate_quota(quota):
    int_keys = ['maxEndpoints']
    alpha_keys = ['requests.memory', 'limits.memory', 'requests.cpu', 'limits.cpu']
    regex_k8s = '^([+]?[0-9.]+)([eEinumkKMGTP]*[+]?[0-9]*)$'

    test_quota = dict(quota)
    for key, value in quota.items():
        if key in int_keys:
            if not value.isdigit() > 0:
                logger.error('Invalid value {} of {} field: '
                             'must be integer greater than or equal to 0'.format(value, key))
                raise falcon.HTTPBadRequest('Invalid value {} of {} field: '
                                            'must be integer greater than or equal to 0'.
                                            format(value, key))
            test_quota.pop(key)
        if key in alpha_keys:
            if not re.match(regex_k8s, value):
                logger.error('Invalid value {} of {} field. '
                             'Please provide value that matches Kubernetes convention. '
                             'Some example values: '
                             '\'1Gi\', \'200Mi\', \'300m\''.format(value, key))
                raise falcon.HTTPBadRequest('Invalid value {} of {} field. '
                                            'Please provide value that matches '
                                            'Kubernetes convention. Some example values: '
                                            '\'1Gi\', \'200Mi\', \'300m\''.format(value, key))
            test_quota.pop(key)

    if test_quota:
        logger.info("There's some redundant values provided that won't be used:")
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


def get_ingress_external_ip(api_instance: client):
    try:
        api_response = api_instance.read_namespaced_service(ING_NAME, ING_NAMESPACE)
        ip = api_response.status.load_balancer.ingress[0].ip
        port = api_response.spec.ports[-1].port
    except Exception as e:
        logger.error('An error occurred during getting ingress ip: {}'
                     .format(e))
        raise falcon.HTTPInternalServerError("Internal Server Error")
    try:
            ipaddress.ip_address(ip)
            port = int(port)
    except ValueError as e:
        logger.error('An error occurred during ip validation: {}'
                     .format(e))
        raise falcon.HTTPInternalServerError('Internal Server Error')
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

