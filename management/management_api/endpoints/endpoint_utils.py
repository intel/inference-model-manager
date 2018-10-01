from kubernetes.client.rest import ApiException

from management_api.utils.errors_handling import KubernetesCreateException, \
    KubernetesDeleteException, KubernetesUpdateException, \
    KubernetesGetException
from management_api.utils.logger import get_logger
from management_api.utils.kubernetes_resources import get_ingress_external_ip, \
    get_k8s_api_custom_client, get_k8s_api_client, get_k8s_apps_api_client,\
    validate_quota_compliance, transform_quota
from management_api.config import CRD_GROUP, CRD_VERSION, CRD_PLURAL,\
    CRD_API_VERSION, CRD_KIND, PLATFORM_DOMAIN, DELETE_BODY, REPLICA_FAILURE
from management_api.utils.errors_handling import TenantDoesNotExistException
from management_api.tenants.tenants_utils import tenant_exists


logger = get_logger(__name__)


def create_endpoint(parameters: dict, namespace: str):
    spec = parameters
    metadata = {"name": parameters['endpointName']}
    body = {"apiVersion": CRD_API_VERSION, "kind": CRD_KIND, "spec": spec, "metadata": metadata}
    custom_obj_api_instance = get_k8s_api_custom_client()
    api_instance = get_k8s_api_client()
    validate_quota_compliance(api_instance, namespace=namespace,
                              endpoint_quota=parameters.get('resources', {}))
    parameters['resources'] = transform_quota(parameters['resources'])
    try:
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
    ip, port = get_ingress_external_ip(api_instance)
    address = "{ip}:{port}".format(ip=ip, port=port)
    path = "{endpoint_name}-{namespace}.{platform_domain}".format(endpoint_name=endpoint_name,
                                                                  namespace=namespace,
                                                                  platform_domain=PLATFORM_DOMAIN)
    data_for_request = {'address': address, 'opts': path}

    return data_for_request


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

    return endpoint_url


def update_endpoint(parameters: dict, namespace: str):
    custom_obj_api_instance = get_k8s_api_custom_client()
    try:
        endpoint_object = custom_obj_api_instance. \
            get_namespaced_custom_object(CRD_GROUP, CRD_VERSION, namespace, CRD_PLURAL,
                                         parameters['endpointName'])
    except ApiException as apiException:
        raise KubernetesGetException('endpoint', apiException)

    endpoint_object['spec']['modelName'] = parameters['modelName']
    endpoint_object['spec']['modelVersion'] = parameters['modelVersion']
    if 'resources' in parameters:
        endpoint_object['spec']['resources'] = transform_quota(parameters['resources'])
    try:
        custom_obj_api_instance.patch_namespaced_custom_object(
            CRD_GROUP, CRD_VERSION, namespace, CRD_PLURAL, parameters['endpointName'],
            endpoint_object)
    except ApiException as apiException:
        raise KubernetesUpdateException('endpoint', apiException)

    endpoint_url = create_url_to_service(parameters['endpointName'], namespace)
    return endpoint_url


def list_endpoints(namespace: str):
    if not tenant_exists(namespace):
        raise TenantDoesNotExistException(tenant_name=namespace)
    apps_api_instance = get_k8s_apps_api_client()
    try:
        deployments = apps_api_instance.list_namespaced_deployment(namespace)
    except ApiException as apiException:
        raise KubernetesGetException('endpoint', apiException)
    endpoints_name_status = get_endpoints_name_status(deployments, namespace)
    logger.info(endpoints_name_status)
    return endpoints_name_status


def get_endpoints_name_status(deployments, namespace):
    deployments = deployments.to_dict()['items']
    name_status = "There's no endpoints present in {} tenant".format(namespace)
    if not deployments == []:
        endpoints_name_status = list()
        for deployment in deployments:
            endpoint_name_status = dict()
            name = deployment['metadata']['labels']['endpoint']
            endpoint_name_status['name'] = name
            conditions = deployment['status']['conditions']
            endpoint_name_status['status'], endpoint_name_status['message'] = \
                get_endpoints_status(conditions)
            endpoints_name_status.append(endpoint_name_status)
        name_status = 'Endpoints present in {} tenant: {}'.\
            format(namespace, endpoints_name_status)
    return name_status


def get_endpoints_status(conditions):
    message = "Endpoint is up and running"
    for condition in conditions:
        if condition['status'] == 'True':
            status = condition['type']
            if status == REPLICA_FAILURE:
                message = condition['message']
    return status, message
