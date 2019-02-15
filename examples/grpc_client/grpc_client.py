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
import numpy as np
import tensorflow.contrib.util as tf_contrib_util
import datetime
import argparse

import classes
from grpc_client_utils import prepare_certs, prepare_stub_and_request, MODEL_STATUS_REQUEST, \
                              INFERENCE_REQUEST
from images_2_numpy import load_images_from_list

RPC_TIMEOUT = 30


def get_stub_and_request(endpoint_address, model_name, certs, ssl, target_name, request_type):
    request_type = INFERENCE_REQUEST if request_type is None else request_type
    if ssl:
        server_ca_cert, client_key, client_cert = prepare_certs(server_cert=certs['server_cert'],
                                                                client_key=certs['client_key'],
                                                                client_ca=certs['client_cert'])
        creds = grpc.ssl_channel_credentials(root_certificates=server_ca_cert,
                                             private_key=client_key, certificate_chain=client_cert)
        stub, request = prepare_stub_and_request(address=endpoint_address, model_name=model_name,
                                                 creds=creds, opts=target_name,
                                                 request_type=request_type)
    else:
        stub, request = prepare_stub_and_request(address=endpoint_address, model_name=model_name,
                                                 creds=None, opts=target_name,
                                                 request_type=request_type)
    return stub, request


def get_model_status(stub, request, kwargs):
    result = stub.GetModelStatus(request, RPC_TIMEOUT)  # 5 secs timeout
    print(result)
    return result


def prepare_images(kwargs):
    if kwargs['images_numpy_path']:
        imgs = np.load(kwargs['images_numpy_path'])
    if kwargs['images_list']:
        images = kwargs['images_list'].split(',')
        imgs = load_images_from_list(images, kwargs['image_size'], len(images))
    while int(kwargs['batch_size']) >= imgs.shape[0]:
        imgs = np.append(imgs, imgs, axis=0)
    return imgs


def inference(stub, request, imgs, kwargs):
    print("Start processing:")
    print(f"\tModel name: {kwargs['model_name']}")
    print(f"\tImages in shape: {imgs.shape}\n")
    processing_times = np.zeros((0), int)
    batch_size = int(kwargs['batch_size'])
    if not (kwargs.get('images_number') or kwargs.get('images_number') != 0):
        iterations = int((imgs.shape[0]//batch_size))
    else:
        iterations = int(kwargs.get('images_number'))
    iteration = 0
    while iteration <= iterations:
        for x in range(0, imgs.shape[0] - batch_size + 1, batch_size):
            iteration += 1
            if iteration > iterations:
                break
            end_batch = x + batch_size
            if end_batch > imgs.shape[0]:
                end_batch = imgs.shape[0]
            batch = imgs[x:end_batch]
            request.inputs[kwargs['input_name']].CopyFrom(
                tf_contrib_util.make_tensor_proto(batch, shape=(batch.shape)))
            start_time = datetime.datetime.now()
            result = stub.Predict(request, RPC_TIMEOUT)
            # result includes a dictionary with all model outputs
            end_time = datetime.datetime.now()
            if kwargs['output_name'] not in result.outputs:
                print("Invalid output name", kwargs['output_name'])
                print("Available outputs:")
                for Y in result.outputs:
                    print(Y)
                exit(1)
            duration = (end_time - start_time).total_seconds() * 1000
            processing_times = \
                np.append(processing_times, np.array([int(duration)]))
            output = \
                tf_contrib_util.make_ndarray(result.outputs[kwargs['output_name']])

            print('Iteration {}; Processing time: {} ms; speed {} fps'
                  .format(iteration, round(np.average(duration)),
                          round(1000 * batch_size / np.average(duration))))

            if kwargs['no_imagenet_classes']:
                continue
            print(f'\tImagenet top results in a single batch:')
            for i in range(output.shape[0]):
                single_result = output[[i], ...]
                max_class = np.argmax(single_result)
                print(f'\t\t {i+1} image in batch: {classes.imagenet_classes[max_class]}')

    if kwargs['performance']:
        get_processing_performance(processing_times, batch_size)

    return output


def get_processing_performance(processing_times, batch_size):
    print(f'\nProcessing time for all iterations')
    print(f'Average time: {round(np.average(processing_times), 2):.2f} ms; '
          f'Average speed: {round(1000 * batch_size / np.average(processing_times), 2):.2f} fps')
    print(f'Median time: {round(np.median(processing_times), 2):.2f} ms; '
          f'Median speed: {round(1000 * batch_size / np.median(processing_times), 2):.2f} fps')
    print(f'Max time: {round(np.max(processing_times), 2):.2f} ms; '
          f'Max speed: {round(1000 * batch_size / np.max(processing_times), 2):.2f} fps')
    print(f'Min time: {round(np.min(processing_times), 2):.2f} ms; '
          f'Min speed: {round(1000 * batch_size / np.min(processing_times), 2):.2f} fps')
    print(f'Time percentile 90: {round(np.percentile(processing_times, 90), 2):.2f} ms; '
          f'Speed percentile 90: '
          f'{round(1000 * batch_size / np.percentile(processing_times, 90), 2):.2f} fps')
    print(f'Time percentile 50: {round(np.percentile(processing_times, 50), 2):.2f} ms; '
          f'Speed percentile 50: '
          f'{round(1000 * batch_size / np.percentile(processing_times, 50), 2):.2f} fps')
    print(f'Time standard deviation: {round(np.std(processing_times), 2):.2f}')
    print(f'Time variance: {round(np.var(processing_times), 2):.2f}')


def main(**kwargs):
    certs = dict()
    certs['server_cert'] = kwargs['server_cert']
    certs['client_cert'] = kwargs['client_cert']
    certs['client_key'] = kwargs['client_key']

    ssl = False if kwargs['no_ssl'] else True
    stub, request = get_stub_and_request(
        kwargs['grpc_address'],
        kwargs['model_name'], certs, ssl, kwargs['target_name'],
        kwargs['request_type'])

    if kwargs['request_type'] == MODEL_STATUS_REQUEST:
        output = get_model_status(stub, request, kwargs)
    else:
        imgs = prepare_images(kwargs)

        if kwargs['transpose_input']:
            imgs = imgs.transpose((0, 3, 1, 2))

        output = inference(stub, request, imgs, kwargs)

    return output


def run_grpc_client():
    parser = argparse.ArgumentParser(
        description='Do requests to Tensorflow Serving using jpg images or images in numpy format')

    parser.add_argument('grpc_address', help='Specify url:port to gRPC service')
    parser.add_argument('model_name', help='Specify model name, must be same as is in service')

    parser.add_argument('--target_name', required=False, default=None,
                        help='Specify to override target name')

    parser.add_argument('--server_cert', help='Path to server certificate')
    parser.add_argument('--client_cert', help='Path to client certificate')
    parser.add_argument('--client_key', help='Path to client key')

    files = parser.add_mutually_exclusive_group(required=True)
    files.add_argument('--images_numpy_path', help='Numpy in shape [n,w,h,c]')
    files.add_argument('--images_list', help='Images in .jpg format')
    files.add_argument('--request_type',
                       help='Set to "status" to get model status (available for tf-serving)')

    parser.add_argument('--input_name', required=False, default='in',
                        help='Input tensor of model. Default: in')
    parser.add_argument('--output_name', required=False, default='out',
                        help='Output tensor of model. Default: out')

    parser.add_argument('--image_size', required=False, default=224,
                        help='Size of images. Default: 224')
    parser.add_argument('--images_number', required=False, default=0,
                        help='Define number of images to inference. '
                             'Specify if you want to use only part of numpy array')
    parser.add_argument('--batch_size', required=False, default=1,
                        help='Number of images in a single request. Default: 1')

    parser.add_argument('--no-ssl', action='store_true', help='Set for non-SSL calls')
    parser.add_argument('--transpose_input', action='store_true',
                        help='Set to make NCHW->NHWC input transposing')
    parser.add_argument('--performance', action='store_true',
                        help='Enable processing performance info')
    parser.add_argument('--no_imagenet_classes', action='store_true',
                        help='Set for models without Imagenet classes')
    kwargs = vars(parser.parse_args())

    main(**kwargs)


if __name__ == "__main__":
    run_grpc_client()
