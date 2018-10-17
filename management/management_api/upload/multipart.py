import json

import falcon

from management_api.utils.parse_request import get_body, get_params, logger
from management_api.tenants.tenants_utils import tenant_exists
from management_api.config import RequiredParameters
from management_api.utils.errors_handling import TenantDoesNotExistException, InvalidParamException
from management_api.upload.multipart_utils import create_upload, get_key, complete_upload, \
    upload_part, abort_upload
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
        logger.info("Key: " + key + "  ID: " + upload_id)
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'uploadId': upload_id})


class WriteMultiModel(object):
    def on_put(self, req, resp):
        namespace = get_namespace(req)
        get_params(req.params, required_keys=RequiredParameters.MULTIPART_WRITE)
        multipart_id = str(req.get_param('uploadId'))

        try:
            part_number = int(req.get_param('partNumber'))
        except (ValueError, TypeError):
            raise InvalidParamException('partNumber', 'Wrong partNumber parameter value')

        key = get_key(req.params)
        logger.info(f"Key: {key} ID: {multipart_id}")
        data = req.stream.read()
        if not tenant_exists(namespace):
            raise TenantDoesNotExistException(tenant_name=namespace)

        part_etag = upload_part(data=data, part_number=part_number, bucket=namespace,
                                key=key, multipart_id=multipart_id)
        logger.info(f"ETag: {part_etag}")
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'ETag': part_etag})


class CompleteMultiModel(object):
    def on_post(self, req, resp):
        namespace = get_namespace(req)
        body = get_body(req)
        get_params(body, required_keys=RequiredParameters.MULTIPART_DONE)
        key = get_key(body)
        if not tenant_exists(namespace):
            raise TenantDoesNotExistException(tenant_name=namespace)

        complete_upload(bucket=namespace, key=key, multipart_id=body['uploadId'],
                        parts=body['parts'])
        resp.status = falcon.HTTP_200
        resp.body = f"Upload with ID: {body['uploadId']} completed successfully"


class AbortMultiModel(object):
    def on_post(self, req, resp):
        namespace = get_namespace(req)
        body = get_body(req)
        get_params(body, required_keys=RequiredParameters.MULTIPART_ABORT)
        key = get_key(body)
        if not tenant_exists(namespace):
            raise TenantDoesNotExistException(tenant_name=namespace)

        abort_upload(bucket=namespace, key=key, multipart_id=body['uploadId'])
        resp.status = falcon.HTTP_200
        resp.body = f"Upload with ID: {body['uploadId']} aborted successfully"
