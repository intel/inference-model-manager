import falcon

from management_api.tenants.tenants_utils import get_body, get_params, \
    is_cert_valid, create_namespace, create_bucket, create_secret
from management_api.config import minio_client


class Tenants(object):
    def on_post(self, req, resp):
        """Handles POST requests"""
        body = get_body(req)
        name, cert, scope = get_params(body)
        if is_cert_valid(cert):
            create_namespace(name)
            create_bucket(minio_client, name)
            create_secret(name, cert)
            resp.status = falcon.HTTP_200
            resp.body = 'Tenant {} created\n'.format(name)

    def on_delete(self, req, resp):
        """Handles DELETE requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = 'Delete completed'
