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

from management_api.upload.multipart import StartMultiModel, CompleteMultiModel, WriteMultiModel, \
    AbortMultiModel
from management_api.tenants import Tenants
from management_api.endpoints import Endpoints, EndpointScale, Endpoint
from management_api.authenticate import Authenticate, Token
from management_api.models import Models

routes = [
    dict(resource=Tenants(), url='/tenants'),
    dict(resource=Endpoints(), url='/tenants/{tenant_name}/endpoints'),
    dict(resource=EndpointScale(), url='/tenants/{tenant_name}/endpoints/{endpoint_name}/replicas'),
    dict(resource=Endpoint(), url='/tenants/{tenant_name}/endpoints/{endpoint_name}'),
    dict(resource=StartMultiModel(), url='/tenants/{tenant_name}/upload/start'),
    dict(resource=WriteMultiModel(), url='/tenants/{tenant_name}/upload'),
    dict(resource=CompleteMultiModel(), url='/tenants/{tenant_name}/upload/done'),
    dict(resource=AbortMultiModel(), url='/tenants/{tenant_name}/upload/abort'),
    dict(resource=Authenticate(), url='/authenticate'),
    dict(resource=Token(), url='/authenticate/token'),
    dict(resource=Models(), url='/tenants/{tenant_name}/models'),
]


def register_routes(app):
    for route in routes:
        app.add_route(route['url'], route['resource'])
