#
# Copyright (c) 2018-2019 Intel Corporation
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
import logging
import numpy
import pytest
import tensorflow as tf
import time
import grpc
import json

sys.path.append(os.path.realpath(os.path.join(os.path.realpath(__file__), '../../../../scripts')))  # noqa
sys.path.append(os.path.realpath(os.path.join(os.path.realpath(__file__), '../../../../examples/grpc_client')))  # noqa

from grpc_client import main
import classes
from grpc_client_utils import prepare_certs, prepare_stub_and_request
from model_upload import upload_model

from e2e_tests.management_api_requests import create_tenant, delete_tenant, create_endpoint, \
    update_endpoint

from e2e_tests.config import MODEL_NAME, TENANT_NAME, CREATE_ENDPOINT_VP, UPDATE_ENDPOINT_VP
from e2e_tests.tf_serving_utils.load_numpy import IMAGES, LABELS
from management_api_tests.authenticate import get_user_token
from config import MANAGEMENT_API_URL, CERT_BAD_CLIENT, CERT_BAD_CLIENT_KEY, CERT_CLIENT, \
    CERT_CLIENT_KEY, CERT_SERVER, SENSIBLE_ENDPOINT_RESOURCES
from conftest import get_all_pods_in_namespace, get_logs_of_pod, list_namespaces, \
    download_saved_model_from_path


class EndpointInfo:
    def __init__(self):
        self.info = None
        self.pod_name = None
        self.url = None
        self.credentials = None


endpoint_info = EndpointInfo()

images = IMAGES
image = numpy.expand_dims(images[0], axis=0)
labels = LABELS
first_label = labels[0]
model_input = "in"
model_output = "out"


def test_create_tenant():
    tenant_response = create_tenant()
    assert tenant_response.text == 'Tenant {} created\n'.format(TENANT_NAME)
    assert tenant_response.status_code == 200
    time.sleep(30)


def test_fail_upload_model():
    headers = {'Authorization': get_user_token()['id_token']}
    params = {
        'model_name': MODEL_NAME,
        'model_version': 1,
        'file_path': os.path.abspath('non-existing-model.pb'),
    }
    url = f"{MANAGEMENT_API_URL}/tenants/{TENANT_NAME}"
    with pytest.raises(Exception):
        upload_model(url, params, headers, 30)


def test_upload_models():
    try:
        headers = {'Authorization': get_user_token()['id_token']}
        params = {
            'model_name': MODEL_NAME,
            'model_version': 1,
            'file_path': os.path.abspath('saved_model.pb'),
        }
        url = f"{MANAGEMENT_API_URL}/tenants/{TENANT_NAME}"

        # resnet_v1_50 upload
        download_saved_model_from_path('https://storage.googleapis.com/inference-eu/models_zoo/'
                                       'resnet_V1_50/saved_model/saved_model.pb')

        upload_model(url, params, headers, 30)
        os.remove('saved_model.pb')

        # resnet_v2_50 upload
        download_saved_model_from_path('https://storage.googleapis.com/inference-eu/models_zoo/'
                                       'resnet_V2_50/saved_model/saved_model.pb')
        params['model_version'] = 2
        upload_model(url, params, headers, 30)
        os.remove('saved_model.pb')
    except Exception as e:
        pytest.fail(f"Unexpected error during upload test: {e.text}")


def filter_serving_logs(raw_log):
    logs = ""
    for line in raw_log.splitlines(True):
        if "aws_logging" not in line:
            logs += line
    return logs


def wait_endpoint_setup():
    start_time = time.time()
    tick = start_time
    running = False
    pod_name = None
    while tick - start_time < 100:
        tick = time.time()
        try:
            all_pods = get_all_pods_in_namespace(TENANT_NAME)
            all_pods.items.sort(key=lambda pod: pod.status.start_time, reverse=True)
            pod_name = all_pods.items[0].metadata.name
            logging.info("Pod name :", pod_name)
            logs = get_logs_of_pod(TENANT_NAME, pod_name)
            logs = filter_serving_logs(logs)
            logging.info(logs)
            if "Running gRPC ModelServer at 0.0.0.0:9000" in logs:
                running = True
                break
        except Exception as e:
            logging.info(e)
            time.sleep(10)
    return running, pod_name


def test_create_endpoint_with_bad_subject_name():
    params = {
        'modelName': MODEL_NAME,
        'modelVersionPolicy': CREATE_ENDPOINT_VP,
        'endpointName': MODEL_NAME + 'endpoint',
        'subjectName': 'bad',
        'resources': SENSIBLE_ENDPOINT_RESOURCES,
        'servingName': 'tf-serving',
    }
    endpoint_response = create_endpoint(params)
    assert "created" in endpoint_response.text
    assert endpoint_response.status_code == 200
    running, pod_name = wait_endpoint_setup()
    assert running is True
    endpoint_info.info = get_url_from_response(endpoint_response)
    endpoint_info.pod_name = pod_name
    return endpoint_response


def perform_inference(rpc_timeout: float):
    stub, request = prepare_stub_and_request(endpoint_info.url, MODEL_NAME,
                                             creds=endpoint_info.credentials)

    request.inputs[model_input].CopyFrom(
        tf.contrib.util.make_tensor_proto(image, shape=image.shape))
    prediction_response = "Failed"
    try:
        prediction_response = stub.Predict(request, rpc_timeout)
    except Exception as e:  # noqa
        logging.info("Prediction failed: " + str(e))
        print(str(e))
        pass
    logs = get_logs_of_pod(TENANT_NAME, endpoint_info.pod_name)
    logging.info(filter_serving_logs(logs))
    return prediction_response


def test_prediction_with_certificates_and_wrong_subject_name():
    time.sleep(10)
    endpoint_info.url = endpoint_info.info
    trusted_cert, trusted_key, trusted_ca = prepare_certs(
        CERT_SERVER,
        CERT_CLIENT_KEY,
        CERT_CLIENT)
    endpoint_info.credentials = grpc.ssl_channel_credentials(root_certificates=trusted_cert,
                                                             private_key=trusted_key,
                                                             certificate_chain=trusted_ca)
    # resnet_v1 test
    prediction_response = perform_inference(10.0)
    assert prediction_response == "Failed"


def test_update_subject_name():
    params = {'subjectName': 'client'}
    endpoint_response = update_endpoint(params)
    assert "patched" in endpoint_response.text
    assert endpoint_response.status_code == 200
    time.sleep(10)
    running, pod_name = wait_endpoint_setup()
    endpoint_info.pod_name = pod_name
    assert running is True
    return endpoint_response


def test_prediction_with_certificates():
    time.sleep(10)
    endpoint_info.url = endpoint_info.info
    trusted_cert, trusted_key, trusted_ca = prepare_certs(
        CERT_SERVER,
        CERT_CLIENT_KEY,
        CERT_CLIENT)
    endpoint_info.credentials = grpc.ssl_channel_credentials(root_certificates=trusted_cert,
                                                             private_key=trusted_key,
                                                             certificate_chain=trusted_ca)
    # resnet_v1 test
    prediction_response = perform_inference(10.0)
    assert not prediction_response == "Failed"
    response = numpy.array(prediction_response.outputs[model_output].float_val)

    max_output = numpy.argmax(response) - 1
    num_label = classes.imagenet_classes[max_output]
    test_label = classes.imagenet_classes[first_label]
    assert max_output == first_label
    assert num_label == test_label
    assert response.size == 1000


def test_prediction_batch_with_certificates():
    time.sleep(10)
    prediction_response = perform_inference(30.0)
    response = numpy.array(prediction_response.outputs[model_output].float_val)

    offset = 1001
    max_outputs = []

    for i in range(0, len(response), offset):
        one_output = response[i:i + offset]
        max_output = numpy.argmax(one_output) - 1
        max_outputs.append(max_output)

    for i in range(len(max_outputs)):
        label = classes.imagenet_classes[max_outputs[i]]
        test_label = classes.imagenet_classes[labels[i]]
        assert max_outputs[i] == labels[i]
        assert label == test_label


def test_update_version_policy():
    params = {'modelVersionPolicy': UPDATE_ENDPOINT_VP}
    endpoint_response = update_endpoint(params)
    assert "patched" in endpoint_response.text
    assert endpoint_response.status_code == 200
    time.sleep(10)
    running, pod_name = wait_endpoint_setup()
    endpoint_info.pod_name = pod_name
    assert running is True
    return endpoint_response


def test_prediction_with_certificates_v2():
    time.sleep(10)
    # resnet_v2_test
    prediction_response = perform_inference(10.0)

    assert not prediction_response == "Failed"
    response = numpy.array(prediction_response.outputs[model_output].float_val)
    assert response.size == 1001


def test_version_not_served():
    stub, request = prepare_stub_and_request(endpoint_info.url, MODEL_NAME,
                                             model_version=1,
                                             creds=endpoint_info.credentials)

    request.inputs[model_input].CopyFrom(
        tf.contrib.util.make_tensor_proto(image, shape=image.shape))
    with pytest.raises(grpc.RpcError) as context:
        stub.Predict(request, 10.0)

    logs = get_logs_of_pod(TENANT_NAME, endpoint_info.pod_name)
    logging.info(filter_serving_logs(logs))

    assert "Servable not found" in context.value.details()


def test_wrong_certificates():
    url = endpoint_info.info

    trusted_cert, wrong_key, wrong_ca = prepare_certs(
        CERT_SERVER,
        CERT_BAD_CLIENT_KEY,
        CERT_BAD_CLIENT)
    creds = grpc.ssl_channel_credentials(root_certificates=trusted_cert,
                                         private_key=wrong_key, certificate_chain=wrong_ca)
    stub, request = prepare_stub_and_request(url, MODEL_NAME, creds=creds)

    numpy_input = numpy.zeros((1, 224, 224, 3), numpy.dtype('<f'))

    request.inputs[model_input].CopyFrom(
        tf.contrib.util.make_tensor_proto(numpy_input, shape=[1, 224, 224, 3]))

    with pytest.raises(grpc.RpcError) as context:
        stub.Predict(request, 10.0)

    assert context.value.details() == 'Received http2 header with status: 403'


def test_no_certificates():
    url = endpoint_info.info
    trusted_cert, _, _ = prepare_certs(CERT_SERVER)
    creds = grpc.ssl_channel_credentials(root_certificates=trusted_cert)
    stub, request = prepare_stub_and_request(url, MODEL_NAME, creds=creds)

    numpy_input = numpy.zeros((1, 224, 224, 3), numpy.dtype('<f'))

    request.inputs[model_input].CopyFrom(
        tf.contrib.util.make_tensor_proto(numpy_input, shape=[1, 224, 224, 3]))

    with pytest.raises(grpc.RpcError) as context:
        stub.Predict(request, 10.0)

    assert context.value.details() == 'Received http2 header with status: 400'


def test_grpc_client():
    url = endpoint_info.info

    output = main(grpc_address=url,
                  target_name=None,
                  server_cert=CERT_SERVER,
                  client_cert=CERT_CLIENT,
                  client_key=CERT_CLIENT_KEY,
                  model_name=MODEL_NAME,
                  input_name='in',
                  output_name='out',
                  images_list=None,
                  images_numpy_path='e2e_tests/tf_serving_utils/images.npy',
                  image_size=224,
                  images_number=2,
                  batch_size=2,
                  no_ssl=None,
                  transpose_input=None,
                  performance='',
                  no_imagenet_classes=None)

    assert output is not None
    assert isinstance(output, numpy.ndarray)


def test_remove_tenant():
    assert delete_tenant().status_code == 200
    start_action = time.time()
    tick = start_action
    ns_exists = None
    while tick - start_action < 100:
        ns_exists = False
        tick = time.time()
        namespaces = list_namespaces()
        logging.info("Listing namespaces")
        for ns in namespaces.items:
            logging.info("Namespace :", ns.metadata.name)
            if TENANT_NAME == ns.metadata.name:
                ns_exists = True
        if not ns_exists:
            break
        logging.info("Waiting 10 sec")
        time.sleep(10)
    assert not ns_exists


def get_url_from_response(endpoint_response):
    res = endpoint_response.text.replace('Endpoint created\n ', '').replace('\'', '\"')
    url = json.loads(res)['url']
    return url
