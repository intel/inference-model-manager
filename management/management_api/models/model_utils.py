#
# Copyright (c) 2018 Intel Corporation
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

import argparse
from kubernetes.client.rest import ApiException
from botocore.exceptions import ClientError

from management_api.config import minio_resource
from management_api.utils.kubernetes_resources import get_k8s_apps_api_client
from management_api.utils.errors_handling import KubernetesGetException, ModelDeleteException, \
    ModelDoesNotExistException, TenantDoesNotExistException, MinioCallException
from management_api.tenants.tenants_utils import tenant_exists


def list_models(namespace: str, id_token):
    if not tenant_exists(namespace, id_token):
        raise TenantDoesNotExistException(namespace)

    apps_api_client = get_k8s_apps_api_client(id_token)
    try:
        deployments = apps_api_client.list_namespaced_deployment(namespace)
    except ApiException as apiException:
        raise KubernetesGetException('deployment', apiException)

    try:
        bucket = minio_resource.Bucket(name=namespace)
    except ClientError as clientError:
        raise MinioCallException(f'An error occurred during bucket reading: {clientError}')

    models = []
    for object in bucket.objects.all():
        if object.size > 0:
            model_path = object.key.split('/')[0].rsplit('-', 1)
            model_name = model_path[0]
            model_version = model_path[-1]
            model_size = object.size
            deployment_count = len(endpoints_using_model(deployments, model_path))
            models.append((model_name, model_version, model_size, deployment_count))

    if not models:
        return f"There are no models present in {namespace} tenant\n"
    else:
        return f'Models in {namespace} tenant ' \
               f'(model name, model version, model size, deployed count): {models}\n'


def delete_model(parameters: dict, namespace: str, id_token):
    if not tenant_exists(namespace, id_token):
        raise TenantDoesNotExistException(namespace)

    model_path = f"{parameters['modelName']}-{parameters['modelVersion']}"
    bucket = minio_resource.Bucket(name=namespace)
    model_in_bucket = bucket.objects.filter(Prefix=model_path)

    if not model_exists(model_in_bucket):
        raise ModelDoesNotExistException(model_path)

    apps_api_client = get_k8s_apps_api_client(id_token)
    try:
        deployments = apps_api_client.list_namespaced_deployment(namespace)
    except ApiException as apiException:
        raise KubernetesGetException('deployment', apiException)

    endpoint_names = endpoints_using_model(deployments, model_path)
    if endpoint_names:
        raise ModelDeleteException(f'model is used by endpoints: {endpoint_names}')

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

    return endpoint_names


def model_exists(model):
    model_keys = sum(1 for _ in model)
    if model_keys == 0:
        return False
    return True


def get_model_base_path(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('tensorflow_model_server')
    parser.add_argument('--port')
    parser.add_argument('--model_name')
    parser.add_argument('--model_base_path')
    model_base_path = parser.parse_args(args.split()).model_base_path.strip('\"').split('/')[-1]
    return model_base_path
