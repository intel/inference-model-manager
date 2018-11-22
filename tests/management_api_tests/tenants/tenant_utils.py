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
from botocore.exceptions import ClientError
from management_api_tests.config import NO_SUCH_BUCKET_EXCEPTION, RESOURCE_NOT_FOUND, \
    CheckResult, TERMINATION_IN_PROGRESS
import logging


def check_bucket_existence(minio_client, bucket):
    try:
        minio_client.list_objects_v2(Bucket=bucket)

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == NO_SUCH_BUCKET_EXCEPTION:
            return CheckResult.RESOURCE_DOES_NOT_EXIST
        logging.error(e)
        return CheckResult.ERROR

    except Exception as e:
        logging.error(e)
        return CheckResult.ERROR

    return CheckResult.RESOURCE_AVAILABLE


def check_namespace_availability(api_instance, namespace):
    response = None
    try:
        response = api_instance.read_namespace_status(namespace)

    except ApiException as apiException:
        if apiException.status == RESOURCE_NOT_FOUND:
            return CheckResult.RESOURCE_DOES_NOT_EXIST
        return CheckResult.ERROR

    except Exception as e:
        logging.error(e)
        return CheckResult.ERROR

    if response and response.status.phase == TERMINATION_IN_PROGRESS:
        return CheckResult.RESOURCE_BEING_DELETED
    return CheckResult.RESOURCE_AVAILABLE


def check_namespaced_secret_existence(api_instance, secret_name, secret_namespace):
    try:
        api_instance.read_namespaced_secret(secret_name, secret_namespace)

    except ApiException as apiException:
        if apiException.status == RESOURCE_NOT_FOUND:
            return CheckResult.RESOURCE_DOES_NOT_EXIST
        return CheckResult.ERROR

    except Exception as e:
        logging.error(e)
        return CheckResult.ERROR
    return CheckResult.RESOURCE_AVAILABLE


def check_copied_secret_data_matching_original(api_instance, secret_name,
                                               original_secret_namespace,
                                               copied_secret_namespace):
    try:
        original_secret = api_instance.read_namespaced_secret(secret_name,
                                                              original_secret_namespace)
        copied_secret = api_instance.read_namespaced_secret(secret_name, copied_secret_namespace)

    except ApiException as apiException:
        if apiException.status == RESOURCE_NOT_FOUND:
            return CheckResult.RESOURCE_DOES_NOT_EXIST
        return CheckResult.ERROR

    except Exception as e:
        logging.error(e)
        return CheckResult.ERROR

    if original_secret.data == copied_secret.data:
        return CheckResult.CONTENTS_MATCHING
    return CheckResult.CONTENTS_MISMATCHING


def check_resource_quota_matching_provided(api_instance, tenant_name, provided_quota):
    try:
        resource_quota = api_instance.read_namespaced_resource_quota(name=tenant_name,
                                                                     namespace=tenant_name)
    except ApiException as apiException:
        if apiException.status == RESOURCE_NOT_FOUND:
            return CheckResult.RESOURCE_DOES_NOT_EXIST
        return CheckResult.ERROR

    except Exception as e:
        logging.error(e)
        return CheckResult.ERROR

    if resource_quota.spec.hard == provided_quota:
        return CheckResult.CONTENTS_MATCHING
    return CheckResult.CONTENTS_MISMATCHING


def check_role_existence(rbac_api_instance, namespace, role):
    response = None
    try:
        response = rbac_api_instance.read_namespaced_role(role, namespace)
    except ApiException as apiException:
        if apiException.status == RESOURCE_NOT_FOUND:
            return CheckResult.RESOURCE_DOES_NOT_EXIST
        return CheckResult.ERROR
    except Exception as e:
        logging.error(e)
        return CheckResult.ERROR
    logging.info(response)
    return CheckResult.RESOURCE_AVAILABLE


def check_rolebinding_existence(rbac_api_instance, namespace, rolebinding):
    response = None
    try:
        response = rbac_api_instance.read_namespaced_role_binding(rolebinding, namespace)
    except ApiException as apiException:
        if apiException.status == RESOURCE_NOT_FOUND:
            return CheckResult.RESOURCE_DOES_NOT_EXIST
        return CheckResult.ERROR
    except Exception as e:
        logging.error(e)
        return CheckResult.ERROR
    logging.info(response)
    return CheckResult.RESOURCE_AVAILABLE
