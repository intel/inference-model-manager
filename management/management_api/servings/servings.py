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
import json

from management_api.servings.servings_utils import list_servings, get_serving


class Servings(object):
    def on_get(self, req, resp):
        response = list_servings(req.params['Authorization'])
        resp.status = falcon.HTTP_OK
        resp.body = json.dumps({'status': 'OK', 'data': response})


class Serving(object):
    def on_get(self, req, resp, serving_name):
        response = get_serving(req.params['Authorization'], serving_name)
        resp.status = falcon.HTTP_OK
        resp.body = json.dumps({'status': 'OK', 'data': response})
