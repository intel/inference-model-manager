#
# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import json
import falcon
from falcon.media.validators import jsonschema

from management_api.utils.logger import get_logger
from management_api.tenants.tenants_utils import tenant_exists
from management_api.utils.errors_handling import TenantDoesNotExistException, \
    MissingParamException, InvalidParamException
from management_api.upload.multipart_utils import create_upload, get_key, complete_upload, \
    upload_part, abort_upload
from management_api.authenticate import get_namespace
from management_api.schemas.uploads import multipart_start_schema, multipart_done_schema,\
    multipart_abort_schema


logger = get_logger(__name__)


class StartMultiModel(object):
    @jsonschema.validate(multipart_start_schema)
    def on_post(self, req, resp, tenant_name):
        namespace = get_namespace(tenant_name)
        body = req.media
        key = get_key(body)
        if not tenant_exists(namespace, id_token=req.get_header('Authorization')):
            raise TenantDoesNotExistException(tenant_name=namespace)

        upload_id = create_upload(bucket=namespace, key=key)
        logger.info("Key: " + key + "  ID: " + upload_id)
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'uploadId': upload_id})


class WriteMultiModel(object):

    def model_put_params_validator(func):
        def func_wrapper(self, req, resp, tenant_name):
            required_keys = ['modelName', 'modelVersion', 'fileName', 'partNumber', 'uploadId']
            for required_key in required_keys:
                if required_key not in req.params:
                    raise MissingParamException(required_key)
            func(self, req, resp, tenant_name)
        return func_wrapper

    @model_put_params_validator
    def on_put(self, req, resp, tenant_name):
        namespace = get_namespace(tenant_name)
        multipart_id = req.get_param('uploadId')
        try:
            part_number = int(req.get_param('partNumber'))
        except (ValueError, TypeError):
            raise InvalidParamException('partNumber', 'Wrong partNumber parameter value')
        key = get_key(req.params)
        logger.info(f"Key: {key} ID: {multipart_id}")
        data = req.stream.read()
        if not tenant_exists(namespace, id_token=req.get_header('Authorization')):
            raise TenantDoesNotExistException(tenant_name=namespace)

        part_etag = upload_part(data=data, part_number=part_number, bucket=namespace,
                                key=key, multipart_id=multipart_id)
        logger.info(f"ETag: {part_etag}")
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'ETag': part_etag})


class CompleteMultiModel(object):
    @jsonschema.validate(multipart_done_schema)
    def on_post(self, req, resp, tenant_name):
        namespace = get_namespace(tenant_name)
        body = req.media
        key = get_key(body)
        if not tenant_exists(namespace, id_token=req.get_header('Authorization')):
            raise TenantDoesNotExistException(tenant_name=namespace)

        complete_upload(bucket=namespace, key=key, multipart_id=body['uploadId'],
                        parts=body['parts'])
        resp.status = falcon.HTTP_200
        resp.body = f"Upload with ID: {body['uploadId']} completed successfully"


class AbortMultiModel(object):
    @jsonschema.validate(multipart_abort_schema)
    def on_post(self, req, resp, tenant_name):
        namespace = get_namespace(tenant_name)
        body = req.media
        key = get_key(body)
        if not tenant_exists(namespace, id_token=req.get_header('Authorization')):
            raise TenantDoesNotExistException(tenant_name=namespace)

        abort_upload(bucket=namespace, key=key, multipart_id=body['uploadId'])
        resp.status = falcon.HTTP_200
        resp.body = f"Upload with ID: {body['uploadId']} aborted successfully"
