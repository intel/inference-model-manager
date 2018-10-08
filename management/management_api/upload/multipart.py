import falcon

from management_api.utils.parse_request import get_body, get_params
from management_api.tenants.tenants_utils import tenant_exists
from management_api.config import RequiredParameters
from management_api.utils.errors_handling import TenantDoesNotExistException
from management_api.upload.multipart_utils import create_upload, get_key, complete_upload, \
    upload_part
from management_api.authenticate import get_namespace


class StartMultiModel(object):
    def on_post(self, req, resp):
        namespace = get_namespace(req)
        body = get_body(req)
        get_params(body, required_keys=RequiredParameters.MULTIPART_START)
        key = get_key(body)
        if not tenant_exists(namespace):
            raise TenantDoesNotExistException(tenant_name=namespace)

        upload_id = create_upload(bucket=namespace, key=key)
        resp.status = falcon.HTTP_200
        resp.body = 'Multipart ID: {} started'.format(upload_id)


class WriteMultiModel(object):
    def on_put(self, req, resp):
        namespace = get_namespace(req)
        get_params(req.params, required_keys=RequiredParameters.MULTIPART_WRITE)
        multipart_id = req.get_param('uploadId')
        part_number = req.get_param('partNumber')
        key = get_key(req.params)
        data = req.stream.read()
        if not tenant_exists(namespace):
            raise TenantDoesNotExistException(tenant_name=namespace)

        upload_part(data=data, part_number=part_number, bucket=namespace,
                    key=key, multipart_id=multipart_id)
        resp.status = falcon.HTTP_200
        resp.body = 'Part {} of upload with ID: {} sent successfully'.format(part_number,
                                                                             multipart_id)


class FinishMultiModel(object):
    def on_post(self, req, resp):
        namespace = get_namespace(req)
        body = get_body(req)
        get_params(body, required_keys=RequiredParameters.MULTIPART_DONE)
        key = get_key(body)
        if not tenant_exists(namespace):
            raise TenantDoesNotExistException(tenant_name=namespace)

        complete_upload(bucket=namespace, key=key, multipart_id=body['multipartId'])
        resp.status = falcon.HTTP_200
        resp.body = 'Multipart ID: {} finished'.format(body['multipartId'])
