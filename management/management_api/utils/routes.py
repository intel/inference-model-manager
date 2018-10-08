from management_api.upload.multipart import StartMultiModel, FinishMultiModel, WriteMultiModel
from management_api.tenants import Tenants
from management_api.endpoints import Endpoints, EndpointScale, EndpointUpdate, EndpointView
from management_api.authenticate import Authenticate, Token

routes = [
    dict(resource=Tenants(), url='/tenants'),
    dict(resource=Endpoints(), url='/endpoints'),
    dict(resource=EndpointScale(), url='/endpoints/{endpoint_name}/scaling'),
    dict(resource=EndpointUpdate(), url='/endpoints/{endpoint_name}/updating'),
    dict(resource=EndpointView(), url='/endpoints/{endpoint_name}/viewing'),
    dict(resource=StartMultiModel(), url='/upload/start'),
    dict(resource=WriteMultiModel(), url='/upload'),
    dict(resource=FinishMultiModel(), url='/upload/done'),
    dict(resource=Authenticate(), url='/authenticate'),
    dict(resource=Token(), url='/authenticate/token'),

]


def register_routes(app):
    for route in routes:
        app.add_route(route['url'], route['resource'])
