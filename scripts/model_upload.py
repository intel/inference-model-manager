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
from requests import urllib3
urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)

def upload_part(url, params, headers, data, parts, verify):
    print("Sending part nr {} of current upload...".format(params['partNumber']))
    response = requests.put(url + "/upload", data, headers=headers, params=params, verify=verify)
    if response.status_code != 200:
        print("Could not upload part nr : {}".format(params['partNumber']))
        raise Exception(response)

    print("Part nr {} of current upload sent successfully".format(params['partNumber']))
    part_etag = response.json()['ETag']
    parts.append({'ETag': part_etag, 'PartNumber': params['partNumber']})


def upload_model(url, params, headers, part_size, verify=False):
    model_name = params['model_name']
    model_version = params['model_version']
    file_path = params['file_path']
    file_name = os.path.basename(file_path)

    # --- Initiating upload
    data = {'modelName': model_name, 'modelVersion': model_version, 'fileName': file_name}
    response = requests.post(url + "/upload/start", json=data, headers=headers, verify=verify)
    if response.status_code != 200:
        print("Could not initiate upload: {}".format(response.text))
        raise Exception(response)
    upload_id = response.json()['uploadId']
    print("Model upload initiated successfully. Upload id = {}".format(upload_id))

    # --- Uploading parts
    try:
        PART_SIZE = part_size * 1048576  # multiply to get size in bytes
        part_number = 1
        parts = []
        params = {'partNumber': part_number,
                  'uploadId': upload_id,
                  'modelName': model_name,
                  'modelVersion': model_version,
                  'fileName': file_name,
                  }
        with open(file_path, 'rb') as file:
            print("Preparing data for part nr {} of current upload...".format(part_number))
            data = file.read(PART_SIZE)
            upload_part(url, params, headers, data, parts, verify=verify)
            while len(data) == PART_SIZE:
                print("Preparing data for part nr {} of current upload...".format(
                    part_number + 1))

                file.seek(part_number * PART_SIZE)
                data = file.read(PART_SIZE)
                part_number += 1
                params['partNumber'] = part_number
                upload_part(url, params, headers, data, parts, verify=verify)
    except (KeyboardInterrupt, Exception) as e:
        # -- Aborting upload
        print("Exception: {}".format(e))
        print("Aborting upload with id: {} ...".format(upload_id))
        data = {'modelName': model_name, 'modelVersion': model_version, 'fileName': file_name,
                'uploadId': upload_id}
        response = requests.post(url + "/upload/abort", json=data, headers=headers, verify=verify)
        if response.status_code != 200:
            print("Could not abort upload: {}".format(response.text))
            raise Exception(response)
        print("Upload with id: {} aborted successfully".format(upload_id))
        if e.__class__ == KeyboardInterrupt:
            return
        else:
            raise

    # --- Completing upload
    print("Completing update with id: {} ...".format(upload_id))
    data = {'modelName': model_name, 'modelVersion': model_version, 'fileName': file_name,
            'uploadId': upload_id, 'parts': parts}
    response = requests.post(url + "/upload/done", json=data, headers=headers, verify=verify)

    if response.status_code != 200:
        print("Could not complete upload: {}".format(response.text))
        raise Exception(response)

    print("Upload with id: {} completed successfully".format(upload_id))
