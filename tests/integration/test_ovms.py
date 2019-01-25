#
# Copyright (c) 2019 Intel Corporation
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
import sys
import grpc
import time
import logging
import json
from config import CERT_CLIENT, CERT_CLIENT_KEY, CERT_SERVER
from tensorflow_serving.apis import get_model_metadata_pb2
from conftest import get_all_pods_in_namespace, get_logs_of_pod

sys.path.append(os.path.realpath(os.path.join(os.path.realpath(__file__), '../../../examples/grpc_client')))  # noqa

from grpc_client_utils import prepare_certs, prepare_stub_and_request


def test_ovms_serving_status(ovms_endpoint):
    ovms_endpoint_response, namespace = ovms_endpoint
    res = ovms_endpoint_response.text.replace('Endpoint created\n ', '').replace('\'', '\"')
    url = json.loads(res)['url']
    start_time = time.time()
    tick = start_time
    running = False
    while tick - start_time < 100:
        tick = time.time()
        try:
            all_pods = get_all_pods_in_namespace(namespace)
            pod_name = all_pods.items[0].metadata.name
            logging.info("Pod name :", pod_name)
            logs = get_logs_of_pod("ovms", pod_name)
            logging.info(logs)
            if "Server listens on port 9000 and will be serving models" in logs:
                running = True
                break
        except Exception as e:
            logging.info(e)
        time.sleep(10)
    assert running is True
    trusted_cert, trusted_key, trusted_ca = prepare_certs(
        CERT_SERVER,
        CERT_CLIENT_KEY,
        CERT_CLIENT)
    creds = grpc.ssl_channel_credentials(root_certificates=trusted_cert, private_key=trusted_key,
                                         certificate_chain=trusted_ca)
    stub, _ = prepare_stub_and_request(url, "", creds=creds)
    request = get_model_metadata_request("ovms_resnet")
    response = stub.GetModelMetadata(request, 10)
    assert "ovms_resnet" == response.model_spec.name


def get_model_metadata_request(model_name, metadata_field="signature_def",
                               version=None):
    request = get_model_metadata_pb2.GetModelMetadataRequest()
    request.model_spec.name = model_name
    if version is not None:
        request.model_spec.version.value = version
    request.metadata_field.append(metadata_field)
    return request
