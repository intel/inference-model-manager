from tenacity import retry, stop_after_attempt, wait_fixed
import logging
from kubernetes import client

from management_api_tests.config import CRD_GROUP, CRD_VERSION, CRD_PLURAL, OperationStatus, \
    CheckResult
from management_api_tests.endpoints.endpoint_utils import check_server_existence, \
    check_server_pods_existence
from management_api_tests.tenants.tenant_utils import check_bucket_existence, \
    check_namespace_availability


class Context(object):

    def __init__(self, k8s_client, k8s_client_custom, minio_resource_client, minio_client):
        self._objects = []
        self.k8s_client_api = k8s_client
        self.k8s_client_custom = k8s_client_custom
        self.minio_resource_client = minio_resource_client
        self.minio_client = minio_client

        self.DELETE_FUNCTIONS = {'tenant': self._delete_namespace_bucket,
                                 'CRD': self._delete_crd_server,
                                 'model': self._delete_model}

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

        deletion_status = self._wait_tenant_deletion(object_to_delete['name'])
        if deletion_status == OperationStatus.SUCCESS:
            logging.info('Tenant {} deleted successfully.'.format(object_to_delete['name']))
        elif deletion_status == OperationStatus.TERMINATED:
            logging.info('Tenant {} status unknown.'.format(object_to_delete['name']))
        else:
            logging.info('Tenant {} deletion timeout.'.format(object_to_delete['name']))
        return OperationStatus.SUCCESS

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def _delete_crd_server(self, object_to_delete):
        delete_body = client.V1DeleteOptions()
        try:
            response = self.k8s_client_custom.delete_namespaced_custom_object(
                CRD_GROUP, CRD_VERSION, object_to_delete['namespace'], CRD_PLURAL,
                object_to_delete['name'], delete_body, grace_period_seconds=0)
        except Exception as e:
            logging.error(e)
            raise

        deletion_status = self._wait_server_deletion(object_to_delete)
        if deletion_status == OperationStatus.SUCCESS:
            logging.info('CRD {} deleted successfully.'.format(object_to_delete['name']))
        elif deletion_status == OperationStatus.TERMINATED:
            logging.info('CRD {} status unknown.'.format(object_to_delete['name']))
        else:
            logging.info('CRD {} deletion timeout.'.format(object_to_delete['name']))
        return response

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def _delete_model(self, object_to_delete):
        bucket = self.minio_resource_client.Bucket(name=object_to_delete['namespace'])
        try:
            for key in bucket.objects.all():
                key.delete()
        except Exception as e:
            logging.error(e)
            raise

    @retry(stop=stop_after_attempt(100), wait=wait_fixed(2))
    def _wait_server_deletion(self, object_to_delete):
        server_status = check_server_existence(
            self.k8s_client_custom, object_to_delete['namespace'], object_to_delete['name'])
        server_pods_status = check_server_pods_existence(
            self.k8s_client_api, object_to_delete['namespace'], object_to_delete['name'], 1)
        completed = (server_status == CheckResult.RESOURCE_DOES_NOT_EXIST and
                     server_pods_status == CheckResult.RESOURCE_DOES_NOT_EXIST)

        if server_status == CheckResult.ERROR or server_pods_status == CheckResult.ERROR:
            logging.error("Error occurred during server status check")
            return OperationStatus.TERMINATED

        if completed:
            return OperationStatus.SUCCESS
        raise Exception

    @retry(stop=stop_after_attempt(100), wait=wait_fixed(2))
    def _wait_tenant_deletion(self, name):
        bucket_status = check_bucket_existence(self.minio_client, name)
        namespace_status = check_namespace_availability(self.k8s_client_api, name)
        completed = (bucket_status == CheckResult.RESOURCE_DOES_NOT_EXIST and
                     namespace_status == CheckResult.RESOURCE_DOES_NOT_EXIST)

        if bucket_status == CheckResult.ERROR or namespace_status == CheckResult.ERROR:
            logging.error("Error occurred during bucket or namespace status check")
            return OperationStatus.TERMINATED

        if completed:
            return OperationStatus.SUCCESS
        raise Exception
