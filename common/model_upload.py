import os

import requests


def upload_part(url, params, headers, data, parts):
    print(f"Sending part nr {params['partNumber']} of current upload...")
    response = requests.put(url + "/upload", data, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Could not upload part nr : {params['partNumber']}")
        raise Exception

    print(f"Part nr {params['partNumber']} of current upload sent successfully")
    part_etag = response.json()['ETag']
    parts.append({'ETag': part_etag, 'PartNumber': params['partNumber']})


def upload_model(url, params, headers, part_size):
    model_name = params['model_name']
    model_version = params['model_version']
    file_path = params['file_path']
    file_name = os.path.basename(file_path)

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

