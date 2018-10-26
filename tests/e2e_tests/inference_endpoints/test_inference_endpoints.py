import os
import sys

import requests

from grpc.beta import implementations
import logging
import numpy
import pytest
import tensorflow as tf
import json
import time
import grpc

sys.path.append(os.path.join(os.path.expanduser("~"), 'inferno-platform/common'))  # noqa
from model_upload import upload_model

from e2e_tests.management_api_requests import create_endpoint, create_tenant
from e2e_tests.config import MODEL_NAME, TENANT_NAME, \
    CERT_BAD_CLIENT, CERT_BAD_CLIENT_KEY, CERT_CLIENT, CERT_CLIENT_KEY, CERT_SERVER
from e2e_tests.tf_serving_utils import classes
from e2e_tests.tf_serving_utils.load_numpy import IMAGES, LABELS
from e2e_tests.tf_serving_utils.endpoint_utils import prepare_certs, prepare_stub_and_request
from management_api_tests.authenticate import get_user_token
from management_api_tests.config import MANAGEMENT_API_URL


images = IMAGES
image = numpy.expand_dims(images[0], axis=0)
labels = LABELS
first_label = labels[0]
model_input = "in"
model_output = "out"


def test_prediction_with_certificates(function_context, minio_client):
    endpoint = prepare_tenant_endpoint(minio_client)
    function_context.add_object(object_type='tenant', object_to_delete={'name': TENANT_NAME})
    function_context.add_object(object_type='CRD',
                                object_to_delete={'name': MODEL_NAME + 'endpoint',
                                                  'namespace': TENANT_NAME})
    opts, address = get_opts_address(endpoint)

    logging.info('Waiting for endpoint running...')
    time.sleep(40)

    trusted_cert, trusted_key, trusted_ca = prepare_certs(
        CERT_SERVER,
        CERT_CLIENT_KEY,
        CERT_CLIENT)
    creds = implementations.ssl_channel_credentials(root_certificates=trusted_cert,
                                                    private_key=trusted_key,
                                                    certificate_chain=trusted_ca)
    stub, request = prepare_stub_and_request(creds, opts, address, MODEL_NAME)

    request.inputs[model_input].CopyFrom(
        tf.contrib.util.make_tensor_proto(image, shape=image.shape))
    prediction_response = stub.Predict(request, 10.0)

    assert prediction_response is not None

    response = numpy.array(prediction_response.outputs[model_output].float_val)

    max_output = numpy.argmax(response) - 1
    num_label = classes.imagenet_classes[max_output]
    test_label = classes.imagenet_classes[first_label]
    assert max_output == first_label
    assert num_label == test_label


def test_prediction_batch_with_certificates(function_context, minio_client):
    endpoint = prepare_tenant_endpoint(minio_client)
    function_context.add_object(object_type='tenant', object_to_delete={'name': TENANT_NAME})
    function_context.add_object(object_type='CRD',
                                object_to_delete={'name': MODEL_NAME + 'endpoint',
                                                  'namespace': TENANT_NAME})
    opts, address = get_opts_address(endpoint)

    logging.info('Waiting for endpoint running...')
    time.sleep(40)

    trusted_cert, trusted_key, trusted_ca = prepare_certs(
        CERT_SERVER,
        CERT_CLIENT_KEY,
        CERT_CLIENT)
    creds = implementations.ssl_channel_credentials(root_certificates=trusted_cert,
                                                    private_key=trusted_key,
                                                    certificate_chain=trusted_ca)
    stub, request = prepare_stub_and_request(creds, opts, address, MODEL_NAME)

    request.inputs[model_input].CopyFrom(
        tf.contrib.util.make_tensor_proto(images, shape=images.shape))
    prediction_response = stub.Predict(request, 10.0)

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


def test_wrong_certificates(function_context, minio_client):
    endpoint = prepare_tenant_endpoint(minio_client)
    function_context.add_object(object_type='tenant', object_to_delete={'name': TENANT_NAME})
    function_context.add_object(object_type='CRD',
                                object_to_delete={'name': MODEL_NAME + 'endpoint',
                                                  'namespace': TENANT_NAME})
    opts, address = get_opts_address(endpoint)

    logging.info('Waiting for endpoint running...')
    time.sleep(40)

    trusted_cert, wrong_key, wrong_ca = prepare_certs(
        CERT_SERVER,
        CERT_BAD_CLIENT_KEY,
        CERT_BAD_CLIENT)
    creds = implementations.ssl_channel_credentials(root_certificates=trusted_cert,
                                                    private_key=wrong_key,
                                                    certificate_chain=wrong_ca)
    stub, request = prepare_stub_and_request(creds, opts, address, MODEL_NAME)

    numpy_input = numpy.zeros((1, 224, 224, 3), numpy.dtype('<f'))

    request.inputs[model_input].CopyFrom(
        tf.contrib.util.make_tensor_proto(numpy_input, shape=[1, 224, 224, 3]))

    with pytest.raises(grpc.RpcError) as context:
        stub.Predict(request, 10.0)

    assert context.value.details() == 'Received http2 header with status: 403'


def test_no_certificates(function_context, minio_client):
    endpoint = prepare_tenant_endpoint(minio_client)
    function_context.add_object(object_type='tenant', object_to_delete={'name': TENANT_NAME})
    function_context.add_object(object_type='CRD',
                                object_to_delete={'name': MODEL_NAME + 'endpoint',
                                                  'namespace': TENANT_NAME})
    opts, address = get_opts_address(endpoint)

    time.sleep(40)

    trusted_cert, _, _ = prepare_certs(CERT_SERVER)
    creds = implementations.ssl_channel_credentials(root_certificates=trusted_cert)
    stub, request = prepare_stub_and_request(creds, opts, address, MODEL_NAME)

    numpy_input = numpy.zeros((1, 224, 224, 3), numpy.dtype('<f'))

    request.inputs[model_input].CopyFrom(
        tf.contrib.util.make_tensor_proto(numpy_input, shape=[1, 224, 224, 3]))

    with pytest.raises(grpc.RpcError) as context:
        stub.Predict(request, 10.0)

    assert context.value.details() == 'Received http2 header with status: 400'


def prepare_tenant_endpoint(minio_client):
    tenant_response = create_tenant()
    assert tenant_response.text == 'Tenant {} created\n'.format(TENANT_NAME)
    assert tenant_response.status_code == 200
    response = requests.get('https://storage.googleapis.com/inference-eu/models_zoo/'
                            'resnet_V1_50/saved_model/saved_model.pb')
    with open('saved_model.pb', 'wb') as f:
        f.write(response.content)

    headers = {'Authorization': get_user_token()['id_token']}
    params = {
        'model_name': 'e2emodel',
        'model_version': 1,
        'file_path': os.path.abspath('saved_model.pb'),
    }
    url = f"{MANAGEMENT_API_URL}/tenants/test"

    upload_model(url, params, headers, 500)
    os.remove('saved_model.pb')
    endpoint_response = create_endpoint()
    assert endpoint_response.status_code == 200
    assert "created" in endpoint_response.text
    return endpoint_response


def get_opts_address(endpoint_response):
    res = endpoint_response.text.replace('Endpoint created\n ', '').replace('\'', '\"')
    opts = json.loads(res)['opts']
    address = json.loads(res)['address']
    return opts, address
