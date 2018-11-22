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
