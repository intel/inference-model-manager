import falcon
from falcon.media.validators import jsonschema

from management_api.authenticate import get_namespace
from management_api.utils.parse_request import get_body
from management_api.models.model_utils import list_models, delete_model
from management_api.schemas.loadschema import model_delete_schema


class Models(object):
    def on_get(self, req, resp):
        namespace = get_namespace(req)
        response = list_models(namespace)
        resp.status = falcon.HTTP_OK
        resp.body = response

    @jsonschema.validate(model_delete_schema)
    def on_delete(self, req, resp):
        """Handles DELETE requests"""
        namespace = get_namespace(req)
        body = get_body(req)
        response = delete_model(body, namespace)
        resp.status = falcon.HTTP_OK
        resp.body = f'Model deleted: {response}\n'
