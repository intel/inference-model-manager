import falcon

from management_api.tenants.tenants_utils import get_body, get_params, \
    initial_cert_validation, create_namespace, create_bucket, create_secret


class Tenants(object):
    def on_post(self, req, resp):
        """Handles POST requests"""
        body = get_body(req)
        name, cert, scope = get_params(body)
        initial_cert_validation(cert)
        create_namespace(name)
        create_bucket(name)
        create_secret(name, cert)

        resp.status = falcon.HTTP_200
        resp.body = 'Namespace {} created\n'.format(name)

    def on_delete(self, req, resp):
        """Handles DELETE requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = 'Delete completed'
