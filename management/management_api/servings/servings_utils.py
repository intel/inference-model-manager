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

from kubernetes.client.rest import ApiException

from management_api.config import CRD_NAMESPACE
from management_api.tenants.tenants_utils import is_namespace_available
from management_api.utils.errors_handling import KubernetesGetException, \
    ResourceIsNotAvailableException
from management_api.utils.kubernetes_resources import get_k8s_api_client


def list_servings(id_token):
    if not is_namespace_available(CRD_NAMESPACE, id_token):
        raise ResourceIsNotAvailableException('namespace', CRD_NAMESPACE)

    api_client = get_k8s_api_client(id_token)
    try:
        config_maps = api_client.list_namespaced_config_map(CRD_NAMESPACE, pretty='true')
    except ApiException as apiException:
        raise KubernetesGetException('config map', apiException)

    crd_config_maps = []
    for item in config_maps.to_dict()['items']:
        crd_config_maps.append(item['metadata']['name'])

    return crd_config_maps


def get_serving(id_token, serving_name):
    if not is_namespace_available(CRD_NAMESPACE, id_token):
        raise ResourceIsNotAvailableException('namespace', CRD_NAMESPACE)

    api_client = get_k8s_api_client(id_token)
    try:
        config_map = api_client.read_namespaced_config_map(serving_name, CRD_NAMESPACE,
                                                           pretty='true')
    except ApiException as apiException:
        raise KubernetesGetException('config map', apiException)

    crd_config_map = dict()
    try:
        crd_config_map = config_map.to_dict()['data']
    except KeyError:
        raise ResourceIsNotAvailableException('serving template configuration', serving_name)

    return crd_config_map
