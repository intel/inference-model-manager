import botocore
from kubernetes.client.rest import ApiException
from botocore.exceptions import ClientError
from management_api_tests.config import NO_SUCH_BUCKET_EXCEPTION, RESOURCE_DOES_NOT_EXIST
import logging


def is_bucket_available(minio_client, bucket):
    try:
        minio_client.list_objects_v2(Bucket=bucket)
    except botocore.exceptions.ClientError as e:
        logging.error(e)
        error_code = e.response['Error']['Code']
        if error_code == NO_SUCH_BUCKET_EXCEPTION:
            return False
    except Exception as e:
        logging.error(e)
    return True


def is_namespace_available(api_instance, namespace):
    response = None
    try:
        response = api_instance.read_namespace_status(namespace)
    except ApiException as apiException:
        if apiException.status == RESOURCE_DOES_NOT_EXIST:
            return False
    except Exception as e:
        logging.error(e)
    if response and response.status.phase == 'Terminating':
        return False
    return True


def does_secret_exist_in_namespace(api_instance, secret_name, secret_namespace):
    response = None
    try:
        response = api_instance.read_namespaced_secret(secret_name, secret_namespace)
    except ApiException as apiException:
        if apiException.status == RESOURCE_DOES_NOT_EXIST:
            return False
    except Exception as e:
        logging.error(e)
    logging.info(response)
    return True


def is_copied_secret_data_matching_original(api_instance, secret_name,
                                            original_secret_namespace,
                                            copied_secret_namespace):
    try:
        original_secret = api_instance.read_namespaced_secret(secret_name,
                                                              original_secret_namespace)
        copied_secret = api_instance.read_namespaced_secret(secret_name, copied_secret_namespace)
    except ApiException as apiException:
        if apiException.status == RESOURCE_DOES_NOT_EXIST:
            return False
    if original_secret.data == copied_secret.data:
        return True
    return False


def is_role_available(rbac_api_instance, namespace, role):
    response = None
    try:
        response = rbac_api_instance.read_namespaced_role(role, namespace)
    except ApiException as apiException:
        if apiException.status == RESOURCE_DOES_NOT_EXIST:
            return False
    except Exception as e:
        logging.error(e)
        return False
    logging.info(response)
    return True


def is_rolebinding_available(rbac_api_instance, namespace, rolebinding):
    response = None
    try:
        response = rbac_api_instance.read_namespaced_role_binding(rolebinding, namespace)
    except ApiException as apiException:
        if apiException.status == RESOURCE_DOES_NOT_EXIST:
            return False
    except Exception as e:
        logging.error(e)
        return False
    logging.info(response)
    return True  
