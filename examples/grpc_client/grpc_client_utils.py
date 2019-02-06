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


import grpc
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc
from tensorflow_serving.apis import get_model_status_pb2
from tensorflow_serving.apis import model_service_pb2_grpc


INFERENCE_REQUEST = 'inference'
MODEL_STATUS_REQUEST = 'status'


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


def prepare_stub_and_request(address, model_name, model_version=None, creds=None, opts=None,
                             request_type=INFERENCE_REQUEST):
    if opts is not None:
        opts = (('grpc.ssl_target_name_override', opts),)
    if creds is not None:
        channel = grpc.secure_channel(address, creds, options=opts)
    else:
        channel = grpc.insecure_channel(address, options=opts)
    request = None
    stub = None
    if request_type == MODEL_STATUS_REQUEST:
        request = get_model_status_pb2.GetModelStatusRequest()
        stub = model_service_pb2_grpc.ModelServiceStub(channel)
    elif request_type == INFERENCE_REQUEST:
        stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
        request = predict_pb2.PredictRequest()
    request.model_spec.name = model_name
    if model_version is not None:
        request.model_spec.version.value = model_version
    return stub, request
