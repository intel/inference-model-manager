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


def get_dex_auth_token(address, port, auth_code, ca_cert_path):
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
