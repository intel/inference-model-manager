from management_api.upload.multipart import StartMultiModel, CompleteMultiModel, WriteMultiModel, \
    AbortMultiModel
from management_api.tenants import Tenants
from management_api.endpoints import Endpoints, EndpointScale, EndpointUpdate, EndpointView
from management_api.authenticate import Authenticate, Token
from management_api.models import Models

routes = [
    dict(resource=Tenants(), url='/tenants'),
    dict(resource=Endpoints(), url='/tenants/{tenant_name}/endpoints'),
    dict(resource=EndpointScale(), url='/tenants/{tenant_name}/endpoints/{endpoint_name}/scaling'),
    dict(resource=EndpointUpdate(),
         url='/tenants/{tenant_name}/endpoints/{endpoint_name}/updating'),
    dict(resource=EndpointView(), url='/tenants/{tenant_name}/endpoints/{endpoint_name}/viewing'),
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
