from retrying import retry
import logging
from kubernetes import client
from kubernetes.client.rest import ApiException
from botocore.exceptions import ClientError
from time import sleep

from management_api_tests.config import CRD_GROUP, CRD_VERSION, CRD_PLURAL, OperationStatus, \
    CheckResult
from management_api_tests.tenants.tenant_utils import check_bucket_existence, \
    check_namespace_availability


class Context(object):

    def __init__(self, k8s_client, k8s_client_custom, minio_resource_client, minio_client):
        self._objects = []
        self.k8s_client_api = k8s_client
        self.k82_client_custom = k8s_client_custom
        self.minio_resource_client = minio_resource_client
        self.minio_client = minio_client

        self.DELETE_FUNCTIONS = {'tenant': self._delete_namespace_bucket,
                                 'CRD': self._delete_crd_server}

    def delete_all_objects(self):
        while len(self._objects) > 0:
            item = self._objects.pop()
            try:
                logging.info("cleaning: {}".format(item['object']))
                item['function'](object_to_delete=item['object'])
            except Exception as e:
                logging.warning("Error while deleting {}: {}".format(item, e))

    def add_object(self, object_type: str, object_to_delete: dict):
        if object_type in self.DELETE_FUNCTIONS:
            ready_object = {'function': self.DELETE_FUNCTIONS[object_type],
                            'object': object_to_delete}
            logging.info("adding: {}".format(object_to_delete))
            self._objects.append(ready_object)
        else:
            logging.info("We cannot match any delete function to this object: "
                         "{}".format(object_to_delete))

    def _delete_namespace_bucket(self, object_to_delete):
        name = object_to_delete['name']
        try:
            bucket = self.minio_resource_client.Bucket(name)
            bucket.objects.all().delete()
            bucket.delete()
        except Exception as e:
            logging.error(e)
            return OperationStatus.FAILURE

        body = client.V1DeleteOptions()
        try:
            self.k8s_client_api.delete_namespace(name, body)
        except Exception as e:
            logging.error(e)
            return OperationStatus.FAILURE

        completed = False
        while not completed:
            sleep(2)
            bucket_status = check_bucket_existence(self.minio_client, name)
            namespace_status = check_namespace_availability(self.k8s_client_api, name)
            completed = (bucket_status == CheckResult.RESOURCE_DOES_NOT_EXIST and
                         namespace_status == CheckResult.RESOURCE_DOES_NOT_EXIST)

            if bucket_status == CheckResult.ERROR or namespace_status == CheckResult.ERROR:
                logging.error("Error occurred during bucket or namespace status check")
                return OperationStatus.TERMINATED

        logging.info('{} deleted.'.format(name))
        return OperationStatus.SUCCESS

    @retry(stop_max_attempt_number=3, wait_fixed=200)
    def _delete_crd_server(self, object_to_delete):
        delete_body = client.V1DeleteOptions()
        response = self.k82_client_custom.delete_namespaced_custom_object(
            CRD_GROUP, CRD_VERSION, object_to_delete['namespace'], CRD_PLURAL,
            object_to_delete['name'], delete_body, grace_period_seconds=0)
        logging.info('CRD {} deleted.'.format(object_to_delete['name']))
        return response
