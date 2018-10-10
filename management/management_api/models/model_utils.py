import argparse
from kubernetes.client.rest import ApiException
from botocore.exceptions import ClientError

from management_api.config import minio_resource, minio_client, RESOURCE_DOES_NOT_EXIST
from management_api.utils.kubernetes_resources import get_k8s_apps_api_client
from management_api.utils.errors_handling import KubernetesGetException, ModelDeleteException, \
    ModelDoesNotExistException, TenantDoesNotExistException
from management_api.tenants.tenants_utils import tenant_exists


def delete_model(parameters: dict, namespace: str):
    if not tenant_exists(namespace):
        raise TenantDoesNotExistException(namespace)

    model_path = f"{parameters['modelName']}-{parameters['modelVersion']}"

    if not model_exists(namespace, model_path):
        raise ModelDoesNotExistException(model_path)

    apps_api_client = get_k8s_apps_api_client()
    try:
        deployments = apps_api_client.list_namespaced_deployment(namespace)
    except ApiException as apiException:
        raise KubernetesGetException('deployment', apiException)

    endpoints_using_model(deployments, model_path)

    response = minio_client.delete_object(Bucket=namespace, Key=model_path)
    return response


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


def model_exists(namespace, model_path):
    try:
        minio_resource.Object(namespace, model_path + '/').load()
    except ClientError as e:
        if e.response['Error']['Code'] == str(RESOURCE_DOES_NOT_EXIST):
            return False
        else:
            raise
    return True


def get_model_base_path(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('./tensorflow_model_server')
    parser.add_argument('--port')
    parser.add_argument('--model_name')
    parser.add_argument('--model_base_path')
    model_base_path = parser.parse_args(args.split()).model_base_path.strip('\"').split('/')[-1]
    return model_base_path
