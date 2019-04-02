#
# Copyright (c) 2018-2019 Intel Corporation
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

import falcon
import json
from falcon.media.validators import jsonschema

from management_api.utils.logger import get_logger
from management_api.config import WarningMessage
from management_api.endpoints.endpoint_utils import create_endpoint, delete_endpoint, \
    scale_endpoint, update_endpoint, view_endpoint, list_endpoints, check_endpoint_model
from management_api.schemas.endpoints import endpoint_post_schema, endpoint_delete_schema, \
    endpoint_update_schema, endpoint_scale_schema


logger = get_logger(__name__)


class Endpoints(object):

    def on_get(self, req, resp, tenant_name):
        namespace = tenant_name
        endpoints = list_endpoints(namespace, id_token=req.params['Authorization'])
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'status': 'OK', 'data': {'endpoints': endpoints}})

    @jsonschema.validate(endpoint_post_schema)
    def on_post(self, req, resp, tenant_name):
        namespace = tenant_name
        body = req.media
        endpoint_url = create_endpoint(parameters=body, namespace=namespace,
                                       id_token=req.params['Authorization'])
        resp.status = falcon.HTTP_200
        model_existence = check_endpoint_model(namespace, body["modelName"])
        warning_message = '' if model_existence else \
            WarningMessage.MODEL_AVAILABILITY.format(body["modelName"])
        logger.warning(warning_message)
        resp.body = json.dumps({'status': 'CREATED', 'data': {'url': endpoint_url,
                                                              'warning': warning_message}})

    @jsonschema.validate(endpoint_delete_schema)
    def on_delete(self, req, resp, tenant_name):
        namespace = tenant_name
        body = req.media
        endpoint_url = delete_endpoint(parameters=body, namespace=namespace,
                                       id_token=req.params['Authorization'])
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'status': 'DELETED', 'data': {'url': endpoint_url}})


class EndpointScale(object):
    @jsonschema.validate(endpoint_scale_schema)
    def on_patch(self, req, resp, tenant_name, endpoint_name):
        namespace = tenant_name
        body = req.media
        endpoint_url = scale_endpoint(parameters=body, namespace=namespace,
                                      endpoint_name=endpoint_name,
                                      id_token=req.params['Authorization'])

        message = 'Endpoint {} patched successfully. New values: {}\n'.format(endpoint_url, body)
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'status': 'PATCHED', 'data': {'url': endpoint_url, 'values': body}})
        logger.info(message)


class Endpoint(object):
    def on_get(self, req, resp, tenant_name, endpoint_name):
        namespace = tenant_name
        endpoint = view_endpoint(endpoint_name=endpoint_name, namespace=namespace,
                                 id_token=req.params['Authorization'])
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'status': 'OK', 'data': {'url': endpoint}})

    @jsonschema.validate(endpoint_update_schema)
    def on_patch(self, req, resp, tenant_name, endpoint_name):
        namespace = tenant_name
        body = req.media
        endpoint_url = update_endpoint(body, namespace, endpoint_name,
                                       id_token=req.params['Authorization'])
        message = 'Endpoint {} patched successfully. New values: {}\n'.format(endpoint_url, body)
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'status': 'PATCHED', 'data': {'url': endpoint_url, 'values': body}})
        logger.info(message)
