import os
import sys
import logging
import numpy
import pytest
import requests
import tensorflow as tf
import time
import grpc
import json

sys.path.append(os.path.realpath(os.path.join(os.path.realpath(__file__), '../../../../common')))  # noqa
sys.path.append(os.path.realpath(os.path.join(os.path.realpath(__file__), '../../../../scripts')))  # noqa
sys.path.append(os.path.realpath(os.path.join(os.path.realpath(__file__), '../../../../examples/grpc_client')))  # noqa

from grpc_client import main
import classes
from endpoint_utils import prepare_certs, prepare_stub_and_request
from model_upload import upload_model

from e2e_tests.management_api_requests import create_endpoint, create_tenant, delete_tenant

from e2e_tests.config import MODEL_NAME, TENANT_NAME, \
    CERT_BAD_CLIENT, CERT_BAD_CLIENT_KEY, CERT_CLIENT, CERT_CLIENT_KEY, CERT_SERVER
from e2e_tests.tf_serving_utils.load_numpy import IMAGES, LABELS
from management_api_tests.authenticate import get_user_token
from management_api_tests.config import MANAGEMENT_API_URL
from conftest import get_all_pods_in_namespace, get_logs_of_pod, list_namespaces


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


def test_upload_model():
    try:
        response = requests.get('https://storage.googleapis.com/inference-eu/models_zoo/'
                                'resnet_V1_50/saved_model/saved_model.pb')
        with open('saved_model.pb', 'wb') as f:
            f.write(response.content)

        headers = {'Authorization': get_user_token()['id_token']}
        params = {
            'model_name': MODEL_NAME,
            'model_version': 1,
            'file_path': os.path.abspath('saved_model.pb'),
        }
        url = f"{MANAGEMENT_API_URL}/tenants/{TENANT_NAME}"

        upload_model(url, params, headers, 30)
        os.remove('saved_model.pb')

    except Exception as e:
        pytest.fail(f"Unexpected error during upload test {e}")


def filter_serving_logs(raw_log):
    logs = ""
    for line in raw_log.splitlines(True):
        if "aws_logging" not in line:
            logs += line
    return logs


def test_create_endpoint():
    endpoint_response = create_endpoint()
    assert "created" in endpoint_response.text
    assert endpoint_response.status_code == 200
    start_time = time.time()
    tick = start_time
    running = False
    pod_name = None
    while tick - start_time < 100:
        tick = time.time()
        try:
            all_pods = get_all_pods_in_namespace(TENANT_NAME)
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
    assert running is True
    test_create_endpoint.endpoint_info = get_opts_address(endpoint_response)
    test_create_endpoint.pod_name = pod_name
    return endpoint_response


test_create_endpoint.endpoint_info = None
test_create_endpoint.pod_name = None


def test_prediction_with_certificates():
    opts, address = test_create_endpoint.endpoint_info

    trusted_cert, trusted_key, trusted_ca = prepare_certs(
        CERT_SERVER,
        CERT_CLIENT_KEY,
        CERT_CLIENT)
    creds = grpc.ssl_channel_credentials(root_certificates=trusted_cert,
                                         private_key=trusted_key, certificate_chain=trusted_ca)
    stub, request = prepare_stub_and_request(address, MODEL_NAME, creds, opts)

    request.inputs[model_input].CopyFrom(
        tf.contrib.util.make_tensor_proto(image, shape=image.shape))
    prediction_response = "Failed"
    try:
        prediction_response = stub.Predict(request, 10.0)
    except: # noqa
        logging.info("Prediction failed")
        pass
    logs = get_logs_of_pod(TENANT_NAME, test_create_endpoint.pod_name)
    logging.info(filter_serving_logs(logs))

    assert not prediction_response == "Failed"
    response = numpy.array(prediction_response.outputs[model_output].float_val)

    max_output = numpy.argmax(response) - 1
    num_label = classes.imagenet_classes[max_output]
    test_label = classes.imagenet_classes[first_label]
    assert max_output == first_label
    assert num_label == test_label


def test_prediction_batch_with_certificates():
    opts, address = test_create_endpoint.endpoint_info

    trusted_cert, trusted_key, trusted_ca = prepare_certs(
        CERT_SERVER,
        CERT_CLIENT_KEY,
        CERT_CLIENT)
    creds = grpc.ssl_channel_credentials(root_certificates=trusted_cert,
                                         private_key=trusted_key, certificate_chain=trusted_ca)
    stub, request = prepare_stub_and_request(address, MODEL_NAME, creds, opts)

    request.inputs[model_input].CopyFrom(
        tf.contrib.util.make_tensor_proto(images, shape=images.shape))

    prediction_response = "Failed"
    try:
        prediction_response = stub.Predict(request, 10.0)
    except: # noqa
        logging.info("Prediction failed")

    logs = get_logs_of_pod(TENANT_NAME, test_create_endpoint.pod_name)
    logging.info(filter_serving_logs(logs))

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


def test_wrong_certificates():
    opts, address = test_create_endpoint.endpoint_info

    trusted_cert, wrong_key, wrong_ca = prepare_certs(
        CERT_SERVER,
        CERT_BAD_CLIENT_KEY,
        CERT_BAD_CLIENT)
    creds = grpc.ssl_channel_credentials(root_certificates=trusted_cert,
                                         private_key=wrong_key, certificate_chain=wrong_ca)
    stub, request = prepare_stub_and_request(address, MODEL_NAME, creds, opts)

    numpy_input = numpy.zeros((1, 224, 224, 3), numpy.dtype('<f'))

    request.inputs[model_input].CopyFrom(
        tf.contrib.util.make_tensor_proto(numpy_input, shape=[1, 224, 224, 3]))

    with pytest.raises(grpc.RpcError) as context:
        stub.Predict(request, 10.0)

    logs = get_logs_of_pod(TENANT_NAME, test_create_endpoint.pod_name)
    logging.info(filter_serving_logs(logs))

    assert context.value.details() == 'Received http2 header with status: 403'


def test_no_certificates():
    opts, address = test_create_endpoint.endpoint_info

    trusted_cert, _, _ = prepare_certs(CERT_SERVER)
    creds = grpc.ssl_channel_credentials(root_certificates=trusted_cert)
    stub, request = prepare_stub_and_request(address, MODEL_NAME, creds, opts)

    numpy_input = numpy.zeros((1, 224, 224, 3), numpy.dtype('<f'))

    request.inputs[model_input].CopyFrom(
        tf.contrib.util.make_tensor_proto(numpy_input, shape=[1, 224, 224, 3]))

    with pytest.raises(grpc.RpcError) as context:
        stub.Predict(request, 10.0)

    logs = get_logs_of_pod(TENANT_NAME, test_create_endpoint.pod_name)
    logging.info(filter_serving_logs(logs))

    assert context.value.details() == 'Received http2 header with status: 400'


def test_grpc_client():
    opts, address = test_create_endpoint.endpoint_info

    output = main(grpc_address=address,
                  endpoint_name=opts,
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
                  no_imagenet=None)

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


def get_opts_address(endpoint_response):
    res = endpoint_response.text.replace('Endpoint created\n ', '').replace('\'', '\"')
    opts = json.loads(res)['opts']
    address = json.loads(res)['address']
    return opts, address
