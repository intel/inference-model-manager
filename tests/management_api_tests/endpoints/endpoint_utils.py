from time import sleep

from retrying import retry

from management_api_tests.config import CRD_GROUP, CRD_PLURAL, CRD_VERSION, CheckResult, \
    RESOURCE_NOT_FOUND, OperationStatus
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


def check_server_update_result(api_instance, namespace, endpoint_name, new_values):
    try:
        api_response = api_instance.read_namespaced_deployment_status(endpoint_name,
                                                                      namespace,
                                                                      pretty="pretty")
    except ApiException as apiException:
        return CheckResult.ERROR

    container = api_response.spec.template.spec.containers.pop()
    arg = container.args.pop()
    quota = container.resources.limits
    quota.update(container.resources.requests)
    model_path = f'{namespace}/{new_values["modelName"]}-{new_values["modelVersion"]}'
    if 'resources' in new_values:
        new_values['resources'] = transform_quota(new_values['resources'])
        for key, value in new_values['resources']:
            if new_values[key] != quota[key]:
                return CheckResult.CONTENTS_MISMATCHING
    if ('--model_name=' + new_values['modelName']) not in arg or (
            '--model_base_path=s3://' + model_path) not in arg:
        return CheckResult.CONTENTS_MISMATCHING
    return CheckResult.CONTENTS_MATCHING


@retry(stop_max_attempt_number=50)
def wait_server_setup(api_instance, namespace, endpoint_name, replicas):
    sleep(2)
    try:
        api_response = api_instance.read_namespaced_deployment_status(endpoint_name,
                                                                      namespace,
                                                                      pretty="pretty")
    except ApiException as apiException:
        return OperationStatus.TERMINATED

    if api_response.status.updated_replicas != replicas:
        return OperationStatus.FAILURE
    if api_response.status.ready_replicas != api_response.status.updated_replicas:
        raise Exception
    return OperationStatus.SUCCESS
