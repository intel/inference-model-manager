import falcon

from management_api.config import CREATE_ENDPOINT_REQUIRED_PARAMETERS, \
    DELETE_ENDPOINT_REQUIRED_PARAMETERS, SCALE_ENDPOINT_REQUIRED_PARAMETERS
from management_api.utils.parse_request import get_body, get_params
from management_api.endpoints.endpoint_utils import create_endpoint, delete_endpoint, \
    create_url_to_service, validate_params, scale_endpoint
from management_api.utils.kubernetes_resources import validate_quota, transform_quota


class Endpoints(object):
    def on_post(self, req, resp):
        """Handles POST requests"""
        # TODO This needs to be replaced with the logic to obtain namespace out of JWT token
        namespace = req.get_header('Authorization')
        body = get_body(req)
        get_params(body, required_keys=CREATE_ENDPOINT_REQUIRED_PARAMETERS)
        validate_params(params=body)
        validate_quota(body.setdefault('resources', {}))
        body['resources'] = transform_quota(body['resources'])
        create_endpoint(parameters=body, namespace=namespace)
        endpoint_url = create_url_to_service(body['endpointName'], namespace=namespace)
        resp.status = falcon.HTTP_200
        resp.body = 'Endpoint {} created\n'.format(endpoint_url)

    def on_delete(self, req, resp):
        """Handles DELETE requests"""
        # TODO This needs to be replaced with the logic to obtain namespace out of JWT token
        namespace = req.get_header('Authorization')
        body = get_body(req)
        get_params(body, required_keys=DELETE_ENDPOINT_REQUIRED_PARAMETERS)
        delete_endpoint(parameters=body, namespace=namespace)
        endpoint_url = create_url_to_service(body['endpointName'], namespace=namespace)
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = 'Endpoint {} deleted\n'.format(endpoint_url)

    def on_patch(self, req, resp):
        """Handles PATCH requests"""
        # TODO This needs to be replaced with the logic to obtain namespace out of JWT token
        namespace = req.get_header('Authorization')
        body = get_body(req)
        get_params(body, required_keys=SCALE_ENDPOINT_REQUIRED_PARAMETERS)
        scale_endpoint(parameters=body, namespace=namespace)
        endpoint_url = create_url_to_service(body['endpointName'], namespace=namespace)
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = 'Endpoint {} scaled. Number of replicas changed to {}\n'.\
            format(endpoint_url, body['replicas'])
