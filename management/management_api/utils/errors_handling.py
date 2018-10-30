import falcon
import traceback
from management_api.utils.logger import get_logger

logger = get_logger(__name__)


class ManagementApiException(Exception):
    @staticmethod
    def handler(ex, req, resp, params):
        logger.error(str(ex))
        raise falcon.HTTPBadRequest(str(ex))


class KubernetesCallException(ManagementApiException):
    def __init__(self, object_name, k8s_api_exception):
        self.object_name = object_name
        self.k8s_api_exception = k8s_api_exception
        super().__init__(k8s_api_exception)

    def form_response(self, message):
        if 400 <= self.k8s_api_exception.status < 500:
            raise falcon.HTTPBadRequest(message)
        else:
            raise falcon.HTTPInternalServerError(message)


class KubernetesCreateException(KubernetesCallException):
    @staticmethod
    def handler(ex, req, resp, params):
        message = "An error occurred during {} creation: {}"
        logger.error(message.format(ex.object_name, str(ex.k8s_api_exception)))
        ex.form_response(message.format(ex.object_name, ex.k8s_api_exception.reason))


class KubernetesDeleteException(KubernetesCallException):
    @staticmethod
    def handler(ex, req, resp, params):
        message = "An error occurred during {} deletion: {}"
        logger.error(message.format(ex.object_name, str(ex.k8s_api_exception)))
        ex.form_response(message.format(ex.object_name, ex.k8s_api_exception.reason))


class KubernetesGetException(KubernetesCallException):
    @staticmethod
    def handler(ex, req, resp, params):
        message = "An error occurred during reading {} object: {}"
        logger.error(message.format(ex.object_name, str(ex.k8s_api_exception)))
        ex.form_response(message.format(ex.object_name, ex.k8s_api_exception.reason))


class KubernetesUpdateException(KubernetesCallException):
    @staticmethod
    def handler(ex, req, resp, params):
        message = "An error occurred during {} update: {}"
        logger.error(message.format(ex.object_name, str(ex.k8s_api_exception)))
        ex.form_response(message.format(ex.object_name, ex.k8s_api_exception.reason))


class MinioCallException(ManagementApiException):
    def __init__(self, message):
        super().__init__("MINIO FAILURE: " + message)

    @staticmethod
    def handler(ex, req, resp, params):
        logger.error(str(ex))
        raise falcon.HTTPInternalServerError(str(ex))


class TenantAlreadyExistsException(ManagementApiException):
    def __init__(self, tenant_name):
        super().__init__()
        self.tenant_name = tenant_name

    @staticmethod
    def handler(ex, req, resp, params):
        message = "Tenant {} already exists".format(ex.tenant_name)
        logger.error(message)
        raise falcon.HTTPConflict(message)


class TenantDoesNotExistException(ManagementApiException):
    def __init__(self, tenant_name):
        super().__init__()
        self.tenant_name = tenant_name

    @staticmethod
    def handler(ex, req, resp, params):
        message = "Tenant {} does not exist".format(ex.tenant_name)
        logger.error(message)
        raise falcon.HTTPNotFound(description=message)


class EndpointDoesNotExistException(ManagementApiException):
    def __init__(self, endpoint_name):
        super().__init__()
        self.endpoint_name = endpoint_name

    @staticmethod
    def handler(ex, req, resp, params):
        message = "Endpoint {} does not exist".format(ex.endpoint_name)
        logger.error(message)
        raise falcon.HTTPNotFound(description=message)


class EndpointsReachedMaximumException(ManagementApiException):
    def __init__(self):
        super().__init__()

    @staticmethod
    def handler(ex, req, resp, params):
        message = "Endpoints have reached the quantity limit"
        logger.error(message)
        raise falcon.HTTPConflict(description=message)


class ModelDoesNotExistException(ManagementApiException):
    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name

    @staticmethod
    def handler(ex, req, resp, params):
        message = f"Model {ex.model_name} does not exist"
        logger.error(message)
        raise falcon.HTTPNotFound(description=message)


class InvalidParamException(ManagementApiException):
    def __init__(self, param, error_message, validity_rules_message=None):
        super().__init__(error_message)
        self.validity_rules_message = validity_rules_message
        self.param = param

    @staticmethod
    def handler(ex, req, resp, params):
        response_message = str(ex) + " " + ex.validity_rules_message
        logger.error(str(ex))
        raise falcon.HTTPInvalidParam(response_message, ex.param)


class MissingParamException(ManagementApiException):
    def __init__(self, param):
        super().__init__(param + " parameter required")
        self.param = param


class MissingTokenException(ManagementApiException):
    def __init__(self, err):
        super().__init__("Token error: " + str(err))


class JsonSchemaException(ManagementApiException):
    def __init__(self, ex):
        raise


class ModelDeleteException(ManagementApiException):
    def __init__(self, message):
        super().__init__()
        self.message = message

    @staticmethod
    def handler(ex, req, resp, params):
        message = f"Model delete error: {ex.message}"
        logger.error(message)
        raise falcon.HTTPConflict(description=message)


custom_errors = [ManagementApiException, KubernetesCallException, KubernetesDeleteException,
                 KubernetesCreateException, KubernetesGetException, KubernetesUpdateException,
                 MinioCallException, TenantAlreadyExistsException, TenantDoesNotExistException,
                 InvalidParamException, MissingTokenException, JsonSchemaException,
                 EndpointDoesNotExistException, ModelDeleteException, ModelDoesNotExistException,
                 EndpointsReachedMaximumException]


def default_exception_handler(ex, req, resp, params):

    if hasattr(ex, 'title') and "Failed data validation" in ex.title:
        JsonSchemaException(ex)
    message = "Unexpected error occurred: {}".format(ex)
    logger.error(message + "\nRequest: {}  Params: {}".format(req, params))

    if isinstance(ex, falcon.HTTPUnauthorized):
        raise ex

    if isinstance(ex, falcon.HTTPForbidden):
        raise ex

    stacktrace = traceback.format_exc()
    logger.error(stacktrace)

    raise falcon.HTTPInternalServerError(message)


def add_error_handlers(falcon_api):
    falcon_api.add_error_handler(Exception, default_exception_handler)
    for error in custom_errors:
        falcon_api.add_error_handler(error, error.handler)
