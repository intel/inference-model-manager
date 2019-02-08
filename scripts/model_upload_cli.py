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

import argparse
import json
import os
import time
from os import getenv
from os.path import expanduser, join

from model_upload import upload


def read_config():
    config_path = getenv('IMM_CONFIG_PATH', join(expanduser("~"), '.immconfig'))
    with open(config_path) as config_file:
        config = json.load(config_file)
    return config


def model_version_t(value):
    value = int(value)
    if value <= 0:
        raise argparse.ArgumentTypeError("Model version must be a positive integer")
    return value


def part_size_t(value):
    try:
        value = int(value)
        if value < 5 or value > 5000:
            raise Exception
    except Exception:
        raise argparse.ArgumentTypeError("Part size must be integer between 5 and 5000")
    return value


def main():
    parser = argparse.ArgumentParser(description='Model Uploader')
    parser.add_argument('file_path', type=str,
                        help='Path to file with model to upload')
    parser.add_argument('model_name', type=str,
                        help='Name of uploaded model')
    parser.add_argument('model_version', type=model_version_t,
                        help='Version of uploaded model')
    parser.add_argument('tenant', type=str,
                        help='Tenant which is uploading model')
    parser.add_argument('--part', type=part_size_t, default=30,
                        help='Size of data chunk in MB sent in a single upload request '
                             '(acceptable values: 5-5000, default: 30)')
    parser.add_argument('-k', '--insecure',  help='Insecure connection', action='store_true')

    config = read_config()
    headers = {'Authorization': config['id_token']}
    args = parser.parse_args()
    verify = not args.insecure
    params = {
        'model_name': args.model_name,
        'model_version': args.model_version,
        'file_path': os.path.abspath(args.file_path),
        'tenant': args.tenant
    }
    url = "https://{}:{}/tenants/{}".format(config['management_api_address'],
                                            config['management_api_port'], args.tenant)

    start_time = time.time()
    try:
        upload(url, params, headers, args.part, verify)
    except Exception as e:
        print("Unexpected error ocurred while uploading: {}".format(e))
    end_time = time.time()
    print("Time elapsed: " + str(end_time - start_time))


if __name__ == "__main__":
    main()
