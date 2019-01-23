#
# Copyright (c) 2018-2019 Intel Corporation
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

import os
import re

from kubernetes.client.rest import ApiException

from management_api.utils.errors_handling import KubernetesCreateException, \
    KubernetesDeleteException, KubernetesUpdateException, \
    KubernetesGetException, TenantDoesNotExistException, EndpointDoesNotExistException, \
    EndpointsReachedMaximumException
from management_api.utils.logger import get_logger
from management_api.utils.kubernetes_resources import get_crd_subject_name_and_resources, \
    get_k8s_api_custom_client, get_k8s_api_client, get_k8s_apps_api_client,\
    validate_quota_compliance, transform_quota, get_replicas, endpoint_exists, \
    get_endpoint_status
from management_api.config import CRD_GROUP, CRD_VERSION, CRD_PLURAL, \
    CRD_API_VERSION, CRD_KIND, PLATFORM_DOMAIN, DELETE_BODY, DEFAULT_MODEL_VERSION_POLICY, \
    STATUSES
from management_api.tenants.tenants_utils import tenant_exists


logger = get_logger(__name__)


def normalize_version_policy(version_policy):
    normalized_version_policy = re.sub(r'\s+', '', version_policy)
    normalized_version_policy = re.sub(r'(\d)', r'\1 ', normalized_version_policy)
    return normalized_version_policy


def create_endpoint(parameters: dict, namespace: str, id_token: str):
    if not tenant_exists(namespace, id_token=id_token):
        raise TenantDoesNotExistException(tenant_name=namespace)

    metadata = {"name": parameters['endpointName']}
    body = {"apiVersion": CRD_API_VERSION, "kind": CRD_KIND,
            "spec": parameters, "metadata": metadata}
    api_instance = get_k8s_api_client(id_token)

    if 'servingName' not in parameters:
        parameters['servingName'] = 'tf-serving'
    if 'modelVersionPolicy' not in parameters:
        parameters['modelVersionPolicy'] = DEFAULT_MODEL_VERSION_POLICY
    else:
        parameters['modelVersionPolicy'] = \
            normalize_version_policy(parameters['modelVersionPolicy'])

    if 'resources' in parameters:
        validate_quota_compliance(api_instance, namespace=namespace,
                                  endpoint_quota=parameters['resources'])
        parameters['resources'] = transform_quota(parameters['resources'])

    apps_api_instance = get_k8s_apps_api_client(id_token)
    verify_endpoint_amount(api_instance, apps_api_instance, namespace)

    custom_obj_api_instance = get_k8s_api_custom_client(id_token)
    try:
        custom_obj_api_instance.create_namespaced_custom_object(CRD_GROUP, CRD_VERSION, namespace,
                                                                CRD_PLURAL, body)
    except ApiException as apiException:
        raise KubernetesCreateException('endpoint', apiException)
    endpoint_url = create_url_to_service(parameters['endpointName'], namespace)
    logger.info('Endpoint {} created\n'.format(endpoint_url))
    return endpoint_url


def delete_endpoint(parameters: dict, namespace: str, id_token: str):
    custom_obj_api_instance = get_k8s_api_custom_client(id_token)
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
    port = os.getenv("INFERENCE_PORT", 443)
    path = "{endpoint_name}-{namespace}.{platform_domain}:{inference_port}" \
           .format(endpoint_name=endpoint_name,
                   namespace=namespace,
                   platform_domain=PLATFORM_DOMAIN,
                   inference_port=port)
    data_for_request = {'url': path}

    return data_for_request


def scale_endpoint(parameters: dict, namespace: str, endpoint_name: str, id_token: str):
    custom_obj_api_instance = get_k8s_api_custom_client(id_token)
    try:
        endpoint_object = custom_obj_api_instance. \
            get_namespaced_custom_object(CRD_GROUP, CRD_VERSION, namespace, CRD_PLURAL,
                                         endpoint_name)
    except ApiException as apiException:
        raise KubernetesGetException('endpoint', apiException)

    endpoint_object['spec']['replicas'] = parameters['replicas']

    try:
        custom_obj_api_instance.patch_namespaced_custom_object(
            CRD_GROUP, CRD_VERSION, namespace, CRD_PLURAL, endpoint_name, endpoint_object)
    except ApiException as apiException:
        raise KubernetesUpdateException('endpoint', apiException)

    endpoint_url = create_url_to_service(endpoint_name, namespace)

    return endpoint_url


def update_endpoint(parameters: dict, namespace: str, endpoint_name: str, id_token: str):
    custom_obj_api_instance = get_k8s_api_custom_client(id_token)
    try:
        endpoint_object = custom_obj_api_instance. \
            get_namespaced_custom_object(CRD_GROUP, CRD_VERSION, namespace, CRD_PLURAL,
                                         endpoint_name)
    except ApiException as apiException:
        raise KubernetesGetException('endpoint', apiException)

    if 'modelName' in parameters:
        endpoint_object['spec']['modelName'] = parameters['modelName']
    if 'modelVersionPolicy' in parameters:
        endpoint_object['spec']['modelVersionPolicy'] = \
            normalize_version_policy(parameters['modelVersionPolicy'])
    if 'resources' in parameters:
        endpoint_object['spec']['resources'] = transform_quota(parameters['resources'])
    if 'subjectName' in parameters:
        endpoint_object['spec']['subjectName'] = parameters['subjectName']

    try:
        custom_obj_api_instance.patch_namespaced_custom_object(
            CRD_GROUP, CRD_VERSION, namespace, CRD_PLURAL, endpoint_name, endpoint_object)
    except ApiException as apiException:
        raise KubernetesUpdateException('endpoint', apiException)

    endpoint_url = create_url_to_service(endpoint_name, namespace)
    return endpoint_url


def view_endpoint(endpoint_name: str, namespace: str, id_token: str):
    if not tenant_exists(namespace, id_token=id_token):
        raise TenantDoesNotExistException(tenant_name=namespace)
    if not endpoint_exists(endpoint_name, namespace, id_token):
        raise EndpointDoesNotExistException(endpoint_name=endpoint_name)
    custom_api_instance = get_k8s_api_custom_client(id_token)
    api_instance = get_k8s_api_client(id_token)
    apps_api_instance = get_k8s_apps_api_client(id_token)

    endpoint_status = get_endpoint_status(api_instance=api_instance, namespace=namespace,
                                          endpoint_name=endpoint_name)
    model_path = create_url_to_service(endpoint_name, namespace)
    subject_name, resources = get_crd_subject_name_and_resources(
        custom_api_instance=custom_api_instance, namespace=namespace, endpoint_name=endpoint_name)
    replicas = get_replicas(apps_api_instance=apps_api_instance, namespace=namespace,
                            endpoint_name=endpoint_name)

    view_dict = {'Endpoint status': endpoint_status,
                 'Model path': model_path,
                 'Subject name': subject_name,
                 'Resources': resources,
                 'Replicas': replicas,
                 }
    message = f"Endpoint {endpoint_name} in {namespace} tenant: {view_dict}\n"
    logger.info(message)
    return message


def list_endpoints(namespace: str, id_token: str):
    if not tenant_exists(namespace, id_token=id_token):
        raise TenantDoesNotExistException(tenant_name=namespace)
    apps_api_instance = get_k8s_apps_api_client(id_token)
    try:
        deployments = apps_api_instance.list_namespaced_deployment(namespace)
    except ApiException as apiException:
        raise KubernetesGetException('endpoint', apiException)
    endpoints_name_status = get_endpoints_name_status(deployments, namespace)
    logger.info(endpoints_name_status)
    return endpoints_name_status


def get_endpoints_name_status(deployments, namespace):
    deployments = deployments.items
    name_status = "There's no endpoints present in {} tenant".format(namespace)
    if not deployments == []:
        endpoints_name_status = list()
        for deployment in deployments:
            endpoint_name_status = dict()
            name = deployment.metadata.labels['endpoint']
            endpoint_name_status['name'] = name
            endpoint_name_status['url'] = create_url_to_service(name, namespace)['url']
            endpoint_name_status['status'] = STATUSES[deployment.status.unavailable_replicas,
                                                      deployment.status.available_replicas]
            endpoints_name_status.append(endpoint_name_status)
        name_status = 'Endpoints present in {} tenant: {}\n'.format(
            namespace, endpoints_name_status)
    return name_status


def get_endpoint_number(apps_api_instance, namespace):
    try:
        endpoints = apps_api_instance.list_namespaced_deployment(namespace)
    except ApiException as apiException:
        raise KubernetesGetException('endpoint', apiException)
    endpoint_number = len(endpoints.items)

    return endpoint_number


def verify_endpoint_amount(api_instance, apps_api_instance, namespace):
    try:
        namespace_spec = api_instance.read_namespace(namespace)
    except ApiException as apiException:
        raise KubernetesGetException('namespace', apiException)
    namespace_annotations = namespace_spec.metadata.annotations

    if namespace_annotations and 'maxEndpoints' in namespace_annotations:
        endpoint_number = get_endpoint_number(apps_api_instance, namespace)
        if endpoint_number >= int(namespace_annotations['maxEndpoints']):
            raise EndpointsReachedMaximumException()
