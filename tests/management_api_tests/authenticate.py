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

import os
import requests
import sys

from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from requests_oauthlib import OAuth2Session
from requests import urllib3
urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

dex_baseurl = os.environ.get('DEX_URL', 'http://127.0.0.1:8080')

redirect_uri = 'http://127.0.0.1:5555/callback'
client_id = 'example-app'
client_secret = 'ZXhhbXBsZS1hcHAtc2VjcmV0'

# Credentials for admin
ADMIN_CREDENTIALS = {'login': "sun@example.com", 'password': "sun_pass"}

# Credentials for venus which belongs to test group
VENUS_CREDENTIALS = {'login': "venus@example.com", 'password': "venus_pass"}

# Credentials for mercury which belongs to constellation group
MERCURY_CREDENTIALS = {'login': "mercury@example.com", 'password': "mercury_pass"}


# Requests authentication form provided by dex.
# Path and parameters need to be scrapped from "action" attribute of form tag.
def authenticate(username, password, token=True):
    params = {
        'client_id': 'example-app',
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'groups openid email offline_access',
        }
    resp = requests.get(urljoin(dex_baseurl, '/dex/auth'), params=params)
    soup = BeautifulSoup(resp.text, 'html.parser')

    if not soup.form:
        ldap_url = None
        for a in soup.find_all('a', href=True):
            href = a['href']
            if "auth/ldap" in href:
                ldap_url = href
        ldap_login_action = urljoin(dex_baseurl, ldap_url)
        resp = requests.get(ldap_login_action, params=params)
        soup = BeautifulSoup(resp.text, 'html.parser')

    login_form_action = urljoin(dex_baseurl, soup.form['action'])

    # Sends credentials to authenticate against LDAP through dex.
    data = {'login': username, 'password': password}
    resp = requests.post(login_form_action, data=data,
                         allow_redirects=False)

    # Emulates redirection with code autogenerated in dex.
    # Response received after redirection is subsequent redirection to callback endpoint.
    # It contains authorization code in query string. We scrap it.
    resp = requests.get(urljoin(dex_baseurl, resp.headers['Location']),
                        allow_redirects=False, verify=False)
    query = urlparse(resp.headers['Location']).query
    auth_code = parse_qs(query)['code'][0]

    # Exchanges id_token with authorization code.
    if token:
        oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)
        token = oauth.fetch_token(urljoin(dex_baseurl, '/dex/token'),
                                  code=auth_code,
                                  client_secret=client_secret)
        return token

    return auth_code


user_token = None
admin_token = None


def get_user_token():
    global user_token
    if not user_token:
        user_token = authenticate(VENUS_CREDENTIALS['login'], VENUS_CREDENTIALS['password'])
    return user_token


def get_admin_token():
    global admin_token
    if not admin_token:
        admin_token = authenticate(ADMIN_CREDENTIALS['login'],
                                   ADMIN_CREDENTIALS['password'])
    return admin_token


def get_token(userpass):
    user_password = f'{userpass}_pass'
    return authenticate(userpass + "@example.com", user_password)


if __name__ == "__main__":
    user = sys.argv[1]
    token = None
    arr = user.split(':')
    user = arr[0]
    if len(arr) > 1:
        password = arr[1]
        token = authenticate(user, password) 
    if user == 'admin':
        token = get_admin_token()
    elif user == 'user':
        token = get_user_token()
    if token:
        print(token)
