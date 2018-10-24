import falcon
from falcon.media.validators import jsonschema

from management_api.authenticate import get_namespace
from management_api.models.model_utils import list_models, delete_model
from management_api.schemas.models import model_delete_schema


class Models(object):
    def on_get(self, req, resp, tenant_name):
        namespace = get_namespace(tenant_name)
        response = list_models(namespace)
        resp.status = falcon.HTTP_OK
        resp.body = response

    @jsonschema.validate(model_delete_schema)
    def on_delete(self, req, resp, tenant_name):
        """Handles DELETE requests"""
        namespace = get_namespace(tenant_name)
        body = req.media
        response = delete_model(body, namespace)
        resp.status = falcon.HTTP_OK
        resp.body = f'Model deleted: {response}\n'
