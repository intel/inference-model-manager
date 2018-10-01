import ipaddress
from functools import lru_cache
from kubernetes import config, client
from kubernetes.client.rest import ApiException

from management_api.utils.errors_handling import InvalidParamException, KubernetesGetException
from management_api.utils.logger import get_logger
from management_api.config import ING_NAME, ING_NAMESPACE

logger = get_logger(__name__)


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
            raise InvalidParamException("resources",
                                        "No resources provided.",
                                        'There\'s resource quota specified in {} tenant: {} '
                                        'Please fill resource field with given keys in your request'
                                        .format(namespace, tenant_quota))
        if not tenant_quota.keys() == endpoint_quota.keys():
            missing_pairs = {k: v for k, v in tenant_quota.items()
                             if k not in endpoint_quota.keys()}
            if missing_pairs:
                raise InvalidParamException("resources",
                                            "Missing resources values.",
                                            'You need to provide: {}'
                                            .format(missing_pairs))
    return True


def get_svc_external_ip_port(api_instance: client, label_selector: str, namespace: str):
    try:
        api_response = api_instance.list_namespaced_service(namespace,
                                                            label_selector=label_selector)
    except ApiException as e:
        raise KubernetesGetException('List services', e)
    ports = api_response.items[0].spec.ports
    https = next(item for item in ports if item.name == "https")
    ip = api_response.items[0].status.load_balancer.ingress[0].ip
    ipaddress.ip_address(ip)
    port = int(https.port)
    return ip, port


def get_ingress_external_ip(api_instance: client):
    label_selector = 'app={}'.format(ING_NAME)
    return get_svc_external_ip_port(api_instance=api_instance, namespace=ING_NAMESPACE,
                                    label_selector=label_selector)


def get_dex_external_ip(api_instance: client):
    label_selector = 'app={}'.format('dex')
    namespace = 'default'
    return get_svc_external_ip_port(api_instance=api_instance, namespace=namespace,
                                    label_selector=label_selector)


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


@lru_cache(maxsize=None)
def get_k8s_apps_api_client():
    apps_api_client = client.AppsV1Api(client.ApiClient(get_k8s_configuration()))
    return apps_api_client
