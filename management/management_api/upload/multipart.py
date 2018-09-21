import falcon

from management_api.utils.parse_request import get_body, get_params
from management_api.tenants.tenants_utils import tenant_exists
from management_api.config import RequiredParameters
from management_api.utils.errors_handling import TenantDoesNotExistException
from management_api.upload.multipart_utils import create_upload


class StartMultiModel(object):
    def on_post(self, req, resp):
        """Handles POST requests"""
        # TODO This needs to be replaced with the logic to obtain namespace out of JWT token
        namespace = req.get_header('Authorization')
        body = get_body(req)
        get_params(body, required_keys=RequiredParameters.MULTIPART_START)
        if not tenant_exists(namespace):
            raise TenantDoesNotExistException(tenant_name=namespace)
        key = "{model_name}/{model_version}".format(model_name=body['modelName'],
                                                    model_version=body['modelVersion'])
        upload_id = create_upload(bucket=namespace, key=key)
        resp.status = falcon.HTTP_200
        resp.body = 'Multipart ID: {}'.format(upload_id)


