import falcon
from falcon.media.validators import jsonschema

from management_api.tenants.tenants_utils import create_tenant, delete_tenant
from management_api.utils.parse_request import get_body
from management_api.schemas.loadschema import tenant_post_schema, tenant_delete_schema


class Tenants(object):
    @jsonschema.validate(tenant_post_schema)
    def on_post(self, req, resp):
        """Handles POST requests"""
        body = get_body(req)
        name = create_tenant(parameters=body)
        resp.status = falcon.HTTP_200
        resp.body = 'Tenant {} created\n'.format(name)

    @jsonschema.validate(tenant_delete_schema)
    def on_delete(self, req, resp):
        """Handles DELETE requests"""
        body = get_body(req)
        name = delete_tenant(parameters=body)
        resp.status = falcon.HTTP_200
        resp.body = 'Tenant {} deleted\n'.format(name)
