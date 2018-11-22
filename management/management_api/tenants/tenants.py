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

from management_api.tenants.tenants_utils import list_tenants, create_tenant, delete_tenant
from management_api.utils.logger import get_logger
from management_api.schemas.tenants import tenant_post_schema, tenant_delete_schema

logger = get_logger(__name__)


class Tenants(object):

    def on_get(self, req, resp):
        logger.info("List tenants")
        tenants = list_tenants(id_token=req.get_header('Authorization'))
        resp.status = falcon.HTTP_200
        resp.body = tenants

    @jsonschema.validate(tenant_post_schema)
    def on_post(self, req, resp):
        logger.info("Create new tenant")
        body = req.media
        name = create_tenant(parameters=body, id_token=req.get_header('Authorization'))
        resp.status = falcon.HTTP_200
        resp.body = f'Tenant {name} created\n'

    @jsonschema.validate(tenant_delete_schema)
    def on_delete(self, req, resp):
        body = req.media
        name = delete_tenant(parameters=body, id_token=req.get_header('Authorization'))
        resp.status = falcon.HTTP_200
        resp.body = f'Tenant {name} deleted\n'
