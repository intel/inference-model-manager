from __future__ import print_function
import falcon
import re
from kubernetes.client.rest import ApiException

from management_api.utils.logger import get_logger
from management_api.utils.kubernetes_resources import get_ingress_external_ip, \
    get_k8s_api_custom_client, get_k8s_api_client
from management_api.config import CRD_GROUP, CRD_VERSION, CRD_PLURAL, \
    CRD_API_VERSION, CRD_KIND, PLATFORM_DOMAIN, SUBJECT_NAME_RE, DELETE_BODY

logger = get_logger(__name__)


def create_endpoint(parameters: dict, namespace: str):
    spec = parameters
    metadata = {"name": parameters['endpointName']}
    body = {"apiVersion": CRD_API_VERSION, "kind": CRD_KIND, "spec": spec, "metadata": metadata}
    custom_obj_api_instance = get_k8s_api_custom_client()
    try:
        custom_obj_api_instance.create_namespaced_custom_object(CRD_GROUP, CRD_VERSION, namespace,
                                                                CRD_PLURAL, body)
    except ApiException as e:
        logger.error('An error occurred during endpoint creation: {}'
                     .format(e))
        raise falcon.HTTPBadRequest('An error occurred during endpoint '
                                    'creation: {}'.format(e.reason))
    endpoint_url = create_url_to_service(parameters['endpointName'], namespace)
    logger.info('Endpoint {} created\n'.format(endpoint_url))
    return endpoint_url


def delete_endpoint(parameters: dict, namespace: str):
    custom_obj_api_instance = get_k8s_api_custom_client()
    try:
        custom_obj_api_instance.delete_namespaced_custom_object(
            CRD_GROUP, CRD_VERSION, namespace, CRD_PLURAL, parameters['endpointName'], DELETE_BODY,
            grace_period_seconds=0)
    except ApiException as e:
        logger.error('Error occurred during endpoint deletion: {}'.format(e))
        raise falcon.HTTPBadRequest('Error occurred during endpoint '
                                    'deletion: {}'.format(e.reason))
    endpoint_url = create_url_to_service(parameters['endpointName'], namespace)
    logger.info('Endpoint {} deleted\n'.format(endpoint_url))
    return endpoint_url


def create_url_to_service(endpoint_name, namespace):
    api_instance = get_k8s_api_client()
    ip, port = get_ingress_external_ip(api_instance=api_instance)
    address = "{ip}:{port}".format(ip=ip, port=port)
    path = "{endpoint_name}-{namespace}.{platform_domain}".format(endpoint_name=endpoint_name,
                                                                  namespace=namespace,
                                                                  platform_domain=PLATFORM_DOMAIN)
    data_for_request = {'address': address, 'opts': path}

    return data_for_request


def validate_params(params):
    if not re.match(SUBJECT_NAME_RE, params['subjectName']):
        logger.error('Subject name {} is not valid: must consist  '.format(params['subjectName']))
        raise falcon.HTTPBadRequest('Subject name {} is not valid: must consist'.format(
            params['subjectName']))
    try:
        params['modelVersion'] = int(params['modelVersion'])
        if 'replicas' in params:
            params['replicas'] = int(params['replicas'])
    except ValueError as e:
        logger.error('modelVersion and replicas must be convertible to int')
        raise falcon.HTTPBadRequest('modelVersion and replicas must be convertible to int')


def scale_endpoint(parameters: dict, namespace: str):
    custom_obj_api_instance = get_k8s_api_custom_client()
    try:
        endpoint_object = custom_obj_api_instance. \
            get_namespaced_custom_object(CRD_GROUP, CRD_VERSION, namespace, CRD_PLURAL,
                                         parameters['endpointName'])
    except ApiException as e:
        logger.error('An error occurred during reading endpoint object: {}'
                     .format(e))
        raise falcon.HTTPBadRequest('An error occurred during reading endpoint object:'
                                    ' {}'.format(e.reason))

    endpoint_object['spec']['replicas'] = parameters['replicas']

    try:
        custom_obj_api_instance.patch_namespaced_custom_object(
            CRD_GROUP, CRD_VERSION, namespace, CRD_PLURAL, parameters['endpointName'],
            endpoint_object)
    except ApiException as e:
        logger.error('An error occurred during scaling endpoint: {}'
                     .format(e))
        raise falcon.HTTPBadRequest('An error occurred during scaling endpoint:'
                                    ' {}'.format(e.reason))
    endpoint_url = create_url_to_service(parameters['endpointName'], namespace)
    logger.info('Endpoint {} scaled. Number of replicas changed to {}\n'.format(
        endpoint_url, parameters['replicas']))
    return endpoint_url
