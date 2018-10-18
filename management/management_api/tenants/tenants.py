import falcon
from falcon.media.validators import jsonschema

from management_api.tenants.tenants_utils import create_tenant, delete_tenant
from management_api.utils.logger import get_logger
from management_api.schemas.tenants import tenant_post_schema, tenant_delete_schema

logger = get_logger(__name__)


class Tenants(object):

    @jsonschema.validate(tenant_post_schema)
    def on_post(self, req, resp):
        logger.info("Create new tenant")
        body = req.media
        name = create_tenant(parameters=body)
        resp.status = falcon.HTTP_200
        resp.body = 'Tenant {} created\n'.format(name)

    @jsonschema.validate(tenant_delete_schema)
    def on_delete(self, req, resp):
        body = req.media
        name = delete_tenant(parameters=body)
        resp.status = falcon.HTTP_200
        resp.body = 'Tenant {} deleted\n'.format(name)
