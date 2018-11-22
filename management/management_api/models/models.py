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

import falcon
from falcon.media.validators import jsonschema

from management_api.models.model_utils import list_models, delete_model
from management_api.schemas.models import model_delete_schema


class Models(object):
    def on_get(self, req, resp, tenant_name):
        namespace = tenant_name
        response = list_models(namespace, req.get_header('Authorization'))
        resp.status = falcon.HTTP_OK
        resp.body = response

    @jsonschema.validate(model_delete_schema)
    def on_delete(self, req, resp, tenant_name):
        """Handles DELETE requests"""
        namespace = tenant_name
        body = req.media
        response = delete_model(body, namespace, req.get_header('Authorization'))
        resp.status = falcon.HTTP_OK
        resp.body = f'Model deleted: {response}\n'
