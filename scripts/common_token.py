#
# Copyright (c) 2018-2019 Intel Corporation
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


def get_dex_auth_token(address, port, auth_dict, ca_cert_path, proxy_host=None, proxy_port=None,
                       insecure=False, offline=False):
    conn = None
    context = create_security_context(ca_cert_path, insecure=insecure)
    if proxy_host:
        conn = httplib.HTTPSConnection(proxy_host, proxy_port, context=context)
        conn.set_tunnel(address, port)
    else:
        conn = httplib.HTTPSConnection(address, port, context=context)
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    url = "/authenticate/token?offline=True" if offline else "/authenticate/token"
    conn.request("POST", url, json.dumps(auth_dict), headers)
    response = conn.getresponse()
    data = response.read()
    if response.status == 200:
        dict_data = json.loads(data.decode('utf-8'))
        return dict_data['data']['token']
    else:
        print("Error occurred while trying to get token.")
        sys.exit()


def create_security_context(ca_cert_path=None, insecure=False):
    if insecure:
        return ssl._create_unverified_context()
    return ssl.create_default_context(cafile=ca_cert_path)


def get_dex_auth_url(address, port, ca_cert_path=None, proxy_host=None, proxy_port=None,
                     insecure=False, offline=False):
    conn = None
    context = create_security_context(ca_cert_path, insecure=insecure)
    if proxy_host:
        conn = httplib.HTTPSConnection(proxy_host, proxy_port, context=context)
        conn.set_tunnel(address, port)
    else:
        conn = httplib.HTTPSConnection(address, port, context=context)
    url = "/authenticate?offline=True" if offline else "/authenticate"
    conn.request("GET", url)
    r1 = conn.getresponse()
    dex_auth_url = r1.getheader('location')
    if dex_auth_url is None:
        print("Can`t get dex url.")
        sys.exit()
    return dex_auth_url
