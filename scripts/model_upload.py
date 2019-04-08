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
import shutil
import tarfile

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
    part_etag = response.json()['data']['ETag']
    parts.append({'ETag': part_etag, 'PartNumber': params['partNumber']})


def upload_model(url, params, headers, part_size, verify=False):
    file_path = params['file_path']
    if os.path.isfile(file_path):
        if tarfile.is_tarfile(file_path):
            untar_and_upload(url, params, headers, part_size, verify)
        else:
            upload_file(url, params, headers, part_size, verify)
    elif os.path.isdir(file_path):
        upload_dir(url, params, headers, part_size, verify)
    else:
        raise Exception("Unrecognized type of upload")


def untar_and_upload(url, params, headers, part_size, verify=False):
    tmp_dir = '/tmp/imm'
    tar = tarfile.open(params['file_path'])
    tar.extractall(path=tmp_dir)
    tar.close()
    params['file_path'] = tmp_dir
    upload_dir(url, params, headers, part_size, verify)
    shutil.rmtree(tmp_dir, ignore_errors=True)


def upload_dir(url, params, headers, part_size, verify=False):
    uploaded_tree = []
    for dir_name, subdir_list, file_list in os.walk(params['file_path']):
        print('Found directory: {}'.format(dir_name))
        if len(file_list) == 0 and len(subdir_list) == 1:
            print('Current dir contains only another dir, omitting....')
        else:
            file_path = dir_name
            break

    for dir_name, subdir_list, file_list in os.walk(file_path):
        additional_key = os.path.relpath(dir_name, file_path)
        path = '{}/{}'.format(params['model_name'], params['model_version'])
        if additional_key is not '.':
            params['additional_key'] = additional_key
            print('Found directory: {}'.format(dir_name))
            path += '/{}'.format(params['additional_key'])
        if len(file_list) != 0:
            for file_name in file_list:
                print('Found file: {}'.format(file_name))
                params['file_path'] = os.path.join(dir_name, file_name)
                print('Uploading {} to {}'.format(file_name, path))
                upload_file(url, params, headers, part_size, verify)
                uploaded_tree.append(path + '/' + file_name)
        elif len(file_list) == 0 and len(subdir_list) == 0:
            print('Creating empty directory: {}'.format(path))
            create_empty_dir(url, params, headers, verify)
            uploaded_tree.append(path)
    print('Uploaded to:')
    print('\n'.join(uploaded_tree))


def create_empty_dir(url, params, headers, verify=False):
    data = {'modelName': params['model_name'],
            'modelVersion': params['model_version']}
    if params.get('additional_key'):
        data['key'] = params['additional_key']
    response = requests.post(url + "/upload/dir", json=data, headers=headers, verify=verify)
    if response.status_code != 200:
        print("Could not create directory: {}".format(response.status_code))
        raise Exception(response)
    print('Empty directory created')


def upload_file(url, params, headers, part_size, verify=False):
    model_name = params['model_name']
    model_version = params['model_version']
    file_path = params['file_path']
    file_name = os.path.basename(file_path)
    additional_key = params['additional_key'] if 'additional_key' in params \
                                                 and params['additional_key'] is not None else None

    # --- Initiating upload
    data = {'modelName': model_name, 'modelVersion': model_version, 'fileName': file_name,
            'key': additional_key}
    response = requests.post(url + "/upload/start", json=data, headers=headers, verify=verify)
    if response.status_code != 200:
        print("Could not initiate upload: {}".format(response.text))
        raise Exception(response)
    upload_id = response.json()['data']['uploadId']
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
                  'key': additional_key
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
                'uploadId': upload_id, 'key': additional_key}
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
            'uploadId': upload_id, 'parts': parts, 'key': additional_key}
    response = requests.post(url + "/upload/done", json=data, headers=headers, verify=verify)

    if response.status_code != 200:
        print("Could not complete upload: {}".format(response.text))
        raise Exception(response)

    print("Upload with id: {} completed successfully".format(upload_id))
