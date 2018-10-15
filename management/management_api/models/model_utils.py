import argparse
from kubernetes.client.rest import ApiException

from management_api.config import minio_resource
from management_api.utils.kubernetes_resources import get_k8s_apps_api_client
from management_api.utils.errors_handling import KubernetesGetException, ModelDeleteException, \
    ModelDoesNotExistException, TenantDoesNotExistException
from management_api.tenants.tenants_utils import tenant_exists


def delete_model(parameters: dict, namespace: str):
    if not tenant_exists(namespace):
        raise TenantDoesNotExistException(namespace)

    model_path = f"{parameters['modelName']}-{parameters['modelVersion']}"
    bucket = minio_resource.Bucket(name=namespace)
    model_in_bucket = bucket.objects.filter(Prefix=model_path)

    if not model_exists(model_in_bucket):
        raise ModelDoesNotExistException(model_path)

    apps_api_client = get_k8s_apps_api_client()
    try:
        deployments = apps_api_client.list_namespaced_deployment(namespace)
    except ApiException as apiException:
        raise KubernetesGetException('deployment', apiException)

    endpoints_using_model(deployments, model_path)

    for key in model_in_bucket:
        key.delete()

    return model_path


def endpoints_using_model(deployments, model_path):
    endpoint_names = []
    for item in deployments.to_dict()['items']:
        endpoint_name = item['metadata']['labels']['endpoint']
        arg = item['spec']['template']['spec']['containers'][0]['args'][0]
        model_base_path = get_model_base_path(arg)
        if model_path == model_base_path:
            endpoint_names.append(endpoint_name)
    if endpoint_names:
        raise ModelDeleteException(f'model is used by endpoints: {endpoint_names}')


def model_exists(model):
    model_keys = sum(1 for _ in model)
    if model_keys == 0:
        return False
    return True


def get_model_base_path(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('./tensorflow_model_server')
    parser.add_argument('--port')
    parser.add_argument('--model_name')
    parser.add_argument('--model_base_path')
    model_base_path = parser.parse_args(args.split()).model_base_path.strip('\"').split('/')[-1]
    return model_base_path
