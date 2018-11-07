import json
from os import getenv
from os.path import expanduser, join
from common_token import get_dex_auth_token, save_to_file


def check_cert(cert_path):
    return '' if 'None' is cert_path else cert_path


def read_config(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def main():
    config_file_path = getenv('INFERNO_CONFIG_PATH', join(expanduser("~"), '.inferno'))
    config = read_config(config_file_path)
    ca_cert_path = check_cert(config['ca_cert_path'])
    new_config = get_dex_auth_token(config['management_api_address'], config['management_api_port'],
                                    config['refresh_token'], ca_cert_path)
    new_config.update({'management_api_address': config['management_api_address'],
                       'management_api_port': config['management_api_port']})
    save_to_file(config_file_path, new_config)


if __name__ == '__main__':
    main()
