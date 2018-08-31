from management_api_tests.config import CRD_GROUP, CRD_PLURAL, CRD_VERSION, CheckResult, \
    RESOURCE_NOT_FOUND
from kubernetes.client.rest import ApiException
import logging


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
