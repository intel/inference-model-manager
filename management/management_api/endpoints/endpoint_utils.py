from __future__ import print_function
import falcon
import re
from kubernetes.client.rest import ApiException

from management_api.utils.errors_handling import InvalidParamException, \
    KubernetesCreateException, KubernetesDeleteException, KubernetesUpdateException, \
    KubernetesGetException
from management_api.utils.logger import get_logger
from management_api.utils.kubernetes_resources import get_ingress_external_ip, \
    get_k8s_api_custom_client, get_k8s_api_client, validate_quota_compliance, \
    transform_quota
from management_api.config import CRD_GROUP, CRD_VERSION, CRD_PLURAL, \
    CRD_API_VERSION, CRD_KIND, PLATFORM_DOMAIN, SUBJECT_NAME_RE, DELETE_BODY, ValidityMessage

logger = get_logger(__name__)


def create_endpoint(parameters: dict, namespace: str):
    spec = parameters
    metadata = {"name": parameters['endpointName']}
    body = {"apiVersion": CRD_API_VERSION, "kind": CRD_KIND, "spec": spec, "metadata": metadata}
    custom_obj_api_instance = get_k8s_api_custom_client()
    api_instance = get_k8s_api_client()
    try:
        validate_quota_compliance(api_instance, namespace=namespace,
                                  endpoint_quota=parameters.get('resources', None))
        parameters['resources'] = transform_quota(parameters['resources'])
        custom_obj_api_instance.create_namespaced_custom_object(CRD_GROUP, CRD_VERSION, namespace,
                                                                CRD_PLURAL, body)
    except ApiException as apiException:
        raise KubernetesCreateException('endpoint', apiException)

    endpoint_url = create_url_to_service(parameters['endpointName'], namespace)
    logger.info('Endpoint {} created\n'.format(endpoint_url))
    return endpoint_url


def delete_endpoint(parameters: dict, namespace: str):
    custom_obj_api_instance = get_k8s_api_custom_client()
    try:
        custom_obj_api_instance.delete_namespaced_custom_object(
            CRD_GROUP, CRD_VERSION, namespace, CRD_PLURAL, parameters['endpointName'], DELETE_BODY,
            grace_period_seconds=0)
    except ApiException as apiException:
        raise KubernetesDeleteException('endpoint', apiException)

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
    logger.info("Validating endpoint params...")
    if not re.match(SUBJECT_NAME_RE, params['subjectName']):
        raise InvalidParamException('subjectName', 'Subject name {} is not valid.'.
                                    format(params['subjectName']), ValidityMessage.SUBJECT_NAME)
    try:
        params['modelVersion'] = int(params['modelVersion'])
        if 'replicas' in params:
            params['replicas'] = int(params['replicas'])
    except ValueError as e:
        raise InvalidParamException('modelVersion/replicas', 'Invalid modelVersion or replicas',
                                    ValidityMessage.ENDPOINT_INT_VALUES)


def scale_endpoint(parameters: dict, namespace: str):
    custom_obj_api_instance = get_k8s_api_custom_client()
    try:
        endpoint_object = custom_obj_api_instance. \
            get_namespaced_custom_object(CRD_GROUP, CRD_VERSION, namespace, CRD_PLURAL,
                                         parameters['endpointName'])
    except ApiException as apiException:
        raise KubernetesGetException('endpoint', apiException)

    endpoint_object['spec']['replicas'] = parameters['replicas']

    try:
        custom_obj_api_instance.patch_namespaced_custom_object(
            CRD_GROUP, CRD_VERSION, namespace, CRD_PLURAL, parameters['endpointName'],
            endpoint_object)
    except ApiException as apiException:
        raise KubernetesUpdateException('endpoint', apiException)

    endpoint_url = create_url_to_service(parameters['endpointName'], namespace)
    logger.info('Endpoint {} scaled. Number of replicas changed to {}\n'.format(
        endpoint_url, parameters['replicas']))

    return endpoint_url
