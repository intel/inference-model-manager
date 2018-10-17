import argparse
import json
import os
import time
from os import getenv
from os.path import expanduser, join

import requests


def read_config():
    config_path = getenv('INFERNO_CONFIG_PATH', join(expanduser("~"), '.inferno'))
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


def upload_part(url, params, headers, data, parts):
    print(f"Sending part nr {params['partNumber']} of current upload...")
    response = requests.put(url + "/upload", data, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Could not upload part nr : {params['partNumber']}")
        raise Exception

    print(f"Part nr {params['partNumber']} of current upload sent successfully")
    part_etag = response.json()['ETag']
    parts.append({'ETag': part_etag, 'PartNumber': params['partNumber']})


def main():
    parser = argparse.ArgumentParser(description='Inferno Model Uploader')
    parser.add_argument('file_path', type=str,
                        help='Path to file with model to upload')
    parser.add_argument('model_name', type=str,
                        help='Name of uploaded model')
    parser.add_argument('model_version', type=model_version_t,
                        help='Version of uploaded model')
    parser.add_argument('--part', type=part_size_t, default=50,
                        help='Size of data chunk in MB sent in a single upload request '
                             '(acceptable values: 5-5000, default: 50)')

    config = read_config()
    args = parser.parse_args()
    url = f"http://{config['management_api_address']}:{config['management_api_port']}"
    file_name = os.path.basename(args.file_path)
    model_name = args.model_name
    model_version = args.model_version
    headers = {'Authorization': config['id_token']}

    start_time = time.time()

    # --- Initiating upload
    data = {'modelName': model_name, 'modelVersion': model_version, 'fileName': file_name}
    response = requests.post(url + "/upload/start", json=data, headers=headers)
    if response.status_code != 200:
        print(f"Could not initiate upload: {response.text}")
        return
    upload_id = response.json()['uploadId']
    print(f"Model upload initiated successfully. Upload id = {upload_id}")

    # --- Uploading parts
    try:
        PART_SIZE = args.part * 1048576  # multiply to get size in bytes
        part_number = 1
        parts = []
        params = {'partNumber': part_number,
                  'uploadId': upload_id,
                  'modelName': model_name,
                  'modelVersion': model_version,
                  'fileName': file_name,
                  }
        with open(args.file_path, 'rb') as file:
            print(f"Preparing data for part nr {part_number} of current upload...")
            data = file.read(PART_SIZE)
            upload_part(url, params, headers, data, parts)
            while len(data) == PART_SIZE:
                print(f"Preparing data for part nr {part_number + 1} of current upload...")
                file.seek(part_number * PART_SIZE)
                data = file.read(PART_SIZE)
                part_number += 1
                params['partNumber'] = part_number
                upload_part(url, params, headers, data, parts)
    except (KeyboardInterrupt, Exception):
        # -- Aborting upload
        print(f"Aborting upload with id: {upload_id} ...")
        data = {'modelName': model_name, 'modelVersion': model_version, 'fileName': file_name,
                'uploadId': upload_id}
        response = requests.post(url + "/upload/abort", json=data, headers=headers)
        if response.status_code != 200:
            print(f"Could not abort upload: {response.text}")
        print(f"Upload with id: {upload_id} aborted successfully")
        return

    # --- Completing upload
    print("Completing update with id: {} ...".format(upload_id))
    data = {'modelName': model_name, 'modelVersion': model_version, 'fileName': file_name,
            'uploadId': upload_id, 'parts': parts}
    response = requests.post(url + "/upload/done", json=data, headers=headers)

    if response.status_code != 200:
        print(f"Could not complete upload: {response.text}")
        return

    print(f"Upload with id: {upload_id} completed successfully")
    end_time = time.time()
    print("Time elapsed: " + str(end_time - start_time))


if __name__ == "__main__":
    main()
