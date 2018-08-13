import re
import falcon
import ipaddress
from kubernetes.client.rest import ApiException

from management_api.utils.logger import get_logger
from management_api.config import api_instance, ING_NAME, ING_NAMESPACE

logger = get_logger(__name__)


def validate_quota(quota):
    int_keys = ['maxEndpoints', 'requests.cpu', 'limits.cpu']
    alpha_keys = ['requests.memory', 'limits.memory']
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


def get_ingress_external_ip():
    try:
        api_response = api_instance.read_namespaced_service(ING_NAME, ING_NAMESPACE)
        ip = api_response.status.load_balancer.ingress[0].ip
        port = api_response.spec.ports[-1].port
    except ApiException as e:
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
