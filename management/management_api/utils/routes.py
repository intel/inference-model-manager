from management_api.tenants.tenants import Tenants

routes = [
    dict(resource=Tenants(), url='/tenants')
]


def register_routes(app):
    for route in routes:
        app.add_route(route.pop('url'), route.pop('resource'))
