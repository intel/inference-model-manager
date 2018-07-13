from grpc.beta import implementations
from grpc.framework.interfaces.face import face
import numpy
import tensorflow as tf
import pytest

from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2

import classes
from config import HOST_NAME, HOST_PORT


IMAGES = numpy.load("images.npy")[:2]
IMAGE = numpy.expand_dims(IMAGES[0], axis=0)
LABELS = numpy.load("labels.npy")[:2]
LABEL = LABELS[0]


def prepare_certs(server_cert=None, client_key=None, client_ca=None):
    if server_cert is not None:
        with open(server_cert, 'rb') as f:
            server_cert = f.read()
    if client_key is not None:
        with open(client_key, 'rb') as key:
            client_key = key.read()
    if client_ca is not None:
        with open(client_ca, 'rb') as ca:
            client_ca = ca.read()
    return server_cert, client_key, client_ca


def prepare_stub_and_request(creds):
    channel = implementations.secure_channel(HOST_NAME, HOST_PORT, creds)
    stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)
    request = predict_pb2.PredictRequest()
    request.model_spec.name = 'resnet'
    return stub, request


def test_prediction_with_certificates():
    trusted_cert, trusted_key, trusted_ca = prepare_certs('server.crt', 'client.key', 'ca.crt')
    creds = implementations.ssl_channel_credentials(root_certificates=trusted_cert, private_key=trusted_key, certificate_chain=trusted_ca)
    stub, request = prepare_stub_and_request(creds)

    image = IMAGE
    label = LABEL

    request.inputs['import/input_tensor'].CopyFrom(
        tf.contrib.util.make_tensor_proto(image, shape=image.shape)) 
    prediction_response = stub.Predict(request, 10.0)

    assert prediction_response is not None   

    response = numpy.array(prediction_response.outputs['import/softmax_tensor'].float_val)

    max_output = numpy.argmax(response) - 1
    num_label = classes.imagenet_classes[max_output]
    test_label = classes.imagenet_classes[label]
    assert max_output == label
    assert num_label == test_label


def test_prediction_batch_with_certificates():
    trusted_cert, trusted_key, trusted_ca = prepare_certs('server.crt', 'client.key', 'ca.crt')
    creds = implementations.ssl_channel_credentials(root_certificates=trusted_cert, private_key=trusted_key, certificate_chain=trusted_ca)
    stub, request = prepare_stub_and_request(creds)

    images = IMAGES
    labels = LABELS

    request.inputs['import/input_tensor'].CopyFrom(
        tf.contrib.util.make_tensor_proto(images, shape=images.shape))
    prediction_response = stub.Predict(request, 10.0)

    response = numpy.array(prediction_response.outputs['import/softmax_tensor'].float_val)

    OFFSET = 1001
    max_outputs = []

    for i in xrange(0, len(response), OFFSET):
        one_output = response[i:i + OFFSET]
        max_output = numpy.argmax(one_output) - 1
        max_outputs.append(max_output)
    
    for i in range(len(max_outputs)):
        label = classes.imagenet_classes[max_outputs[i]]
        test_label = classes.imagenet_classes[LABELS[i]]
        assert max_outputs[i] == LABELS[i]
        assert label == test_label


def test_wrong_certificates():
    trusted_cert, wrong_key, wrong_ca = prepare_certs('server.crt', 'wrong-client.key', 'wrong-ca.crt')
    creds = implementations.ssl_channel_credentials(root_certificates=trusted_cert, private_key=wrong_key, certificate_chain=wrong_ca)
    stub, request = prepare_stub_and_request(creds)

    input = numpy.zeros((1, 224, 224, 3), numpy.dtype('<f'))

    request.inputs['import/input_tensor'].CopyFrom(
        tf.contrib.util.make_tensor_proto(input, shape=[1, 224, 224, 3]))

    with pytest.raises(face.CancellationError) as context:   
        prediction_response = stub.Predict(request, 10.0)

    print(context.value.code)
    assert context.value.details == 'Received http2 header with status: 400'


def test_no_certificates():
    trusted_cert, _, _ = prepare_certs('server.crt')
    creds = implementations.ssl_channel_credentials(root_certificates=trusted_cert)
    stub, request = prepare_stub_and_request(creds)

    input = numpy.zeros((1, 224, 224, 3), numpy.dtype('<f'))

    request.inputs['import/input_tensor'].CopyFrom(
        tf.contrib.util.make_tensor_proto(input, shape=[1, 224, 224, 3]))

    with pytest.raises(face.CancellationError) as context:
        prediction_response = stub.Predict(request, 10.0)

    print(context.value.code)
    assert context.value.details == 'Received http2 header with status: 400'

