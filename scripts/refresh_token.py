import json
import sys
from os import getenv
from os.path import expanduser, join
try:
    # Imports for Python 3
    import http.client as httplib
except ImportError:
    # Imports for Python 2
    import httplib


def get_dex_auth_token(address, port, refresh_token):
    conn = httplib.HTTPConnection(address, port)
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    conn.request("POST", "/authenticate/token", json.dumps({'refresh_token': refresh_token}),
                 headers)
    response = conn.getresponse()
    data = response.read()
    if response.status == 200:
        dict_data = json.loads(data.decode('utf-8'))
        return dict_data['data']['token']
    else:
        print("Error occurred while trying to get token.")
        sys.exit()


def read_config(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def save_to_file(file_path, data):
    with open(file_path, 'w') as outfile:
        json.dump(data, outfile)


def main():
    config_file_path = getenv('INFERNO_CONFIG_PATH', join(expanduser("~"), '.inferno'))
    config = read_config(config_file_path)
    new_config = get_dex_auth_token(config['management_api_address'], config['management_api_port'],
                                    config['refresh_token'])
    new_config.update({'management_api_address': config['management_api_address'],
                       'management_api_port': config['management_api_port']})
    save_to_file(config_file_path, new_config)


if __name__ == '__main__':
    main()
