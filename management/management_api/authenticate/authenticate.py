import falcon
import json
from management_api.authenticate.auth_controller import get_auth_controller_url, get_token
from management_api.utils.parse_request import get_body, get_params


class Authenticate():

    def on_get(self, req, resp):
        url = get_auth_controller_url()
        resp.status = falcon.HTTP_308
        resp.set_header('Location', url)


class Token():

    def on_post(self, req, resp):
        body = get_body(req)
        get_params(body, required_keys=['code'])
        auth_code = body['code']
        token = get_token(auth_code=body['code'])
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'status': 'OK', 'data': {'token': token}})

