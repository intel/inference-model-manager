from management_api_tests.config import CRD_GROUP, CRD_PLURAL, CRD_VERSION
from kubernetes.client.rest import ApiException
import logging


def is_replicas_number_correct(custom_obj_api_instance, namespace, endpoint_name, expected_amount):
    try:
        endpoint_object = custom_obj_api_instance. \
            get_namespaced_custom_object(CRD_GROUP, CRD_VERSION, namespace, CRD_PLURAL,
                                         endpoint_name)
    except ApiException as e:
        logging.error('An error occurred during reading endpoint object: {}'.format(e))
        return False
    return endpoint_object['spec']['replicas'] == expected_amount
