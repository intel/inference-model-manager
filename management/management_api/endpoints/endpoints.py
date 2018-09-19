import falcon

from management_api.config import RequiredParameters
from management_api.utils.logger import get_logger
from management_api.utils.parse_request import get_body, get_params
from management_api.endpoints.endpoint_utils import create_endpoint, delete_endpoint, \
    create_url_to_service, validate_params, scale_endpoint, update_endpoint
from management_api.utils.kubernetes_resources import validate_quota

logger = get_logger(__name__)

class Endpoints(object):
    def on_post(self, req, resp):
        """Handles POST requests"""
        # TODO This needs to be replaced with the logic to obtain namespace out of JWT token
        namespace = req.get_header('Authorization')
        body = get_body(req)
        get_params(body, required_keys=RequiredParameters.CREATE_ENDPOINT)
        validate_params(params=body)
        validate_quota(body.setdefault('resources', {}))
        endpoint_url = create_endpoint(parameters=body, namespace=namespace)
        resp.status = falcon.HTTP_200
        resp.body = 'Endpoint created\n {}'.format(endpoint_url)

    def on_delete(self, req, resp):
        """Handles DELETE requests"""
        # TODO This needs to be replaced with the logic to obtain namespace out of JWT token
        namespace = req.get_header('Authorization')
        body = get_body(req)
        get_params(body, required_keys=RequiredParameters.DELETE_ENDPOINT)
        delete_endpoint(parameters=body, namespace=namespace)
        endpoint_url = create_url_to_service(body['endpointName'], namespace=namespace)
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = 'Endpoint {} deleted\n'.format(endpoint_url)


class EndpointPatch(object):

    def patch(self, parameters, namespace):
        pass

    def on_patch(self, req, resp, endpoint_name):
        """Handles PATCH requests"""
        # TODO This needs to be replaced with the logic to obtain namespace out of JWT token
        namespace = req.get_header('Authorization')
        body = get_body(req)
        get_params(body, required_keys=self.required_parameters)
        body['endpointName'] = endpoint_name
        endpoint_url = self.patch(parameters=body, namespace=namespace)
        body.pop('endpointName')
        message = 'Endpoint {} patched successfully. New values: {}\n'.format(endpoint_url, body)
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = message
        logger.info(message)


class EndpointScale(EndpointPatch):
    required_parameters = RequiredParameters.SCALE_ENDPOINT

    def patch(self, parameters, namespace):
        return scale_endpoint(parameters, namespace)


class EndpointUpdate(EndpointPatch):
    required_parameters = RequiredParameters.UPDATE_ENDPOINT

    def patch(self, parameters, namespace):
        return update_endpoint(parameters, namespace)

