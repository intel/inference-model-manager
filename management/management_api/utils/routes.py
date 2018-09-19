from management_api.tenants.tenants import Tenants
from management_api.endpoints.endpoints import Endpoints, EndpointScale, EndpointUpdate
routes = [
    dict(resource=Tenants(), url='/tenants'),
    dict(resource=Endpoints(), url='/endpoints'),
    dict(resource=EndpointScale(), url='/endpoints/{endpoint_name}/scaling'),
    dict(resource=EndpointUpdate(), url='/endpoints/{endpoint_name}/updating'),
]


def register_routes(app):
    for route in routes:
        app.add_route(route.pop('url'), route.pop('resource'))
