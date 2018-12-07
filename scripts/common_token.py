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

import json
import sys
import ssl
try:
    # Imports for Python 3
    import http.client as httplib
except ImportError:
    # Imports for Python 2
    import httplib


def save_to_file(file_path, data):
    with open(file_path, 'w') as outfile:
        json.dump(data, outfile)


def get_dex_auth_token(address, port, auth_code, ca_cert_path, proxy_host=None, proxy_port=None):
    conn = None
    if proxy_host:
        conn = httplib.HTTPSConnection(proxy_host, proxy_port,
                                       context=ssl.create_default_context(cafile=ca_cert_path))
        conn.set_tunnel(address, port)
    else:
        conn = httplib.HTTPSConnection(address, port,
                                       context=ssl.create_default_context(cafile=ca_cert_path))
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    conn.request("POST", "/authenticate/token", json.dumps({'code': auth_code}), headers)
    response = conn.getresponse()
    data = response.read()
    if response.status == 200:
        dict_data = json.loads(data.decode('utf-8'))
        return dict_data['data']['token']
    else:
        print("Error occurred while trying to get token.")
        sys.exit()
