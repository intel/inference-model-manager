#
# Copyright (c) 2019 Intel Corporation
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

from time import sleep


from config import CRD_GROUP, CRD_PLURAL, CRD_VERSION
from management_api_tests.config import CheckResult, RESOURCE_NOT_FOUND, OperationStatus
from kubernetes.client.rest import ApiException
import logging

from management_api_tests.reused import transform_quota


def check_replicas_number_matching_provided(custom_obj_api_instance, namespace, endpoint_name,
                                            provided_number):
    try:
        endpoint_object = custom_obj_api_instance. \
            get_namespaced_custom_object(CRD_GROUP, CRD_VERSION, namespace, CRD_PLURAL,
                                         endpoint_name)
    except ApiException as apiException:
        if apiException.status == RESOURCE_NOT_FOUND:
            return CheckResult.RESOURCE_DOES_NOT_EXIST
        return CheckResult.ERROR

    except Exception as e:
        logging.error('Unexpected error occurred during reading endpoint object: {}'.format(e))
        return CheckResult.ERROR

    if endpoint_object['spec']['replicas'] == provided_number:
        return CheckResult.CONTENTS_MATCHING
    return CheckResult.CONTENTS_MISMATCHING


def check_model_params_matching_provided(custom_obj_api_instance, namespace, endpoint_name,
                                         provided_params):
    try:
        endpoint_object = custom_obj_api_instance. \
            get_namespaced_custom_object(CRD_GROUP, CRD_VERSION, namespace, CRD_PLURAL,
                                         endpoint_name)
    except ApiException as apiException:
        if apiException.status == RESOURCE_NOT_FOUND:
            return CheckResult.RESOURCE_DOES_NOT_EXIST
        return CheckResult.ERROR

    except Exception as e:
        logging.error('Unexpected error occurred during reading endpoint object: {}'.format(e))
        return CheckResult.ERROR

    if 'resources' in provided_params:
        provided_params['resources'] = transform_quota(provided_params['resources'])

    for k, v in provided_params.items():
        if k not in endpoint_object['spec'] or provided_params[k] != endpoint_object['spec'][k]:
            return CheckResult.CONTENTS_MISMATCHING
    return CheckResult.CONTENTS_MATCHING


def check_server_existence(custom_obj_api_instance, namespace, endpoint_name):
    try:
        custom_obj_api_instance. \
            get_namespaced_custom_object(CRD_GROUP, CRD_VERSION, namespace,
                                         CRD_PLURAL, endpoint_name)
    except ApiException as apiException:
        if apiException.status == RESOURCE_NOT_FOUND:
            return CheckResult.RESOURCE_DOES_NOT_EXIST
        return CheckResult.ERROR

    return CheckResult.RESOURCE_AVAILABLE


def check_server_pods_existence(api_instance, namespace, endpoint_name, replicas):
    label_selector = 'endpoint={}'.format(endpoint_name)
    try:
        pods = api_instance.list_namespaced_pod(namespace=namespace,
                                                label_selector=label_selector)
    except ApiException as apiException:
        if apiException.status == RESOURCE_NOT_FOUND:
            return CheckResult.RESOURCE_DOES_NOT_EXIST
        return CheckResult.ERROR
    if len(pods.items) != replicas:
        return CheckResult.RESOURCE_DOES_NOT_EXIST
    return CheckResult.RESOURCE_AVAILABLE


def check_server_update_result(apps_api_instance, api_instance, namespace, endpoint_name,
                               new_values):
    try:
        api_response_deploy = apps_api_instance.read_namespaced_deployment_status(
            endpoint_name, namespace, pretty="pretty")
    except ApiException as apiException:
        return CheckResult.ERROR

    try:
        api_response_configmap = api_instance.read_namespaced_config_map(
            endpoint_name, namespace, pretty="pretty")
    except ApiException as apiException:
        return CheckResult.ERROR

    container = api_response_deploy.spec.template.spec.containers.pop()
    model_config = api_response_configmap.data['tf.conf']
    quota = container.resources.limits
    quota.update(container.resources.requests)
    if 'resources' in new_values:
        new_values['resources'] = transform_quota(new_values['resources'])
        for key, value in new_values['resources']:
            if new_values[key] != quota[key]:
                return CheckResult.CONTENTS_MISMATCHING
    if 'modelName' in new_values:
        model_path = f'{namespace}/{new_values["modelName"]}'
        if ('name:"' + new_values['modelName']) not in model_config or (
                's3://' + model_path) not in model_config:
            return CheckResult.CONTENTS_MISMATCHING
    return CheckResult.CONTENTS_MATCHING


def wait_server_setup(api_instance, namespace, endpoint_name, replicas):
    sleep(5)
    try:
        api_response = api_instance.read_namespaced_deployment_status(endpoint_name,
                                                                      namespace,
                                                                      pretty="pretty")
    except ApiException as apiException:
        return OperationStatus.TERMINATED

    desired_replicas = 0 if api_response.spec.replicas is None else api_response.spec.replicas
    if desired_replicas != replicas:
        print(api_response)
        return OperationStatus.FAILURE

    return OperationStatus.SUCCESS
