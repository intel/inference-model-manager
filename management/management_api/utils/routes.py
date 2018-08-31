from management_api.tenants.tenants import Tenants
from management_api.endpoints.endpoints import Endpoints

routes = [
    dict(resource=Tenants(), url='/tenants'),
    dict(resource=Endpoints(), url='/endpoints')
]


def register_routes(app):
    for route in routes:
        app.add_route(route.pop('url'), route.pop('resource'))
