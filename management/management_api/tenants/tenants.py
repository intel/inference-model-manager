import falcon

from management_api.tenants.tenants_utils import create_tenant, delete_tenant
from management_api.utils.parse_request import get_body, get_params
from management_api.config import CREATE_TENANT_REQUIRED_PARAMETERS, \
    DELETE_TENANT_REQUIRED_PARAMETERS


class Tenants(object):
    def on_post(self, req, resp):
        """Handles POST requests"""
        body = get_body(req)
        get_params(body, required_keys=CREATE_TENANT_REQUIRED_PARAMETERS)
        create_tenant(parameters=body)
        resp.status = falcon.HTTP_200
        resp.body = 'Tenant {} created\n'.format(body['name'])

    def on_delete(self, req, resp):
        """Handles DELETE requests"""
        body = get_body(req)
        get_params(body, DELETE_TENANT_REQUIRED_PARAMETERS)
        delete_tenant(parameters=body)
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = 'Tenant {} deleted\n'.format(body['name'])
