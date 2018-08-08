import falcon

from management_api.tenants.tenants_utils import get_body, get_params, create_tenant


class Tenants(object):
    def on_post(self, req, resp):
        """Handles POST requests"""
        body = get_body(req)
        name, cert, scope, quota = get_params(body)
        create_tenant(name, cert, scope, quota)
        resp.status = falcon.HTTP_200
        resp.body = 'Tenant {} created\n'.format(name)

    def on_delete(self, req, resp):
        """Handles DELETE requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = 'Delete completed'
