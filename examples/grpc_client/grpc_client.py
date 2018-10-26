import grpc
import numpy as np
import tensorflow.contrib.util as tf_contrib_util
import datetime
import argparse

import os
import sys

sys.path.append(os.path.realpath(os.path.join(os.path.realpath(__file__), '../../../common')))

import classes
from endpoint_utils import prepare_certs, prepare_stub_and_request
from images_2_numpy import load_images_from_list


def get_stub_and_request(ssl_flag, endpoint_address, model_name):
    if ssl_flag:
        server_ca_cert_path = './certs/server.crt'
        client_key_path = './certs/client.key'
        client_crt_path = './certs/client.crt'
        server_ca_cert, client_key, client_crt = prepare_certs(server_cert=server_ca_cert_path,
                                                               client_key=client_key_path,
                                                               client_ca=client_crt_path)
        creds = grpc.ssl_channel_credentials(root_certificates=server_ca_cert,
                                         private_key=client_key, certificate_chain=client_crt)
        stub, request = prepare_stub_and_request(endpoint_address, model_name, creds)
    else:
        stub, request = prepare_stub_and_request(endpoint_address, model_name)
    return stub, request


def prepare_images(args):
    if args['images_numpy_path']:
        imgs = np.load(args['images_numpy_path'], mmap_mode='r', allow_pickle=False)
    if args['images_list']:
        images = args['images_list'].split(',')
        imgs = load_images_from_list(images, args['image_size'], len(images))
    return imgs

def inference(model_spec, request_spec, endpoint_address, imgs):
    print(f'Start processing:')
    print(f'\tModel name: {model_spec["model_name"]}')
    print(f'\tImages in shape: {imgs.shape}\n')
    stub, request = get_stub_and_request(request_spec['ssl'], endpoint_address,
                                         model_spec['model_name'])
    processing_times = np.zeros((0), int)
    batch_size = int(request_spec['batch_size'])
    iteration = 0
    for x in range(0, imgs.shape[0], batch_size):
        iteration += 1
        if iteration > imgs.shape[0]: break
        end_batch = x + batch_size
        if end_batch > imgs.shape[0]: end_batch = imgs.shape[0]
        batch = imgs[x:end_batch]
        request.inputs[model_spec['input_name']].CopyFrom(
            tf_contrib_util.make_tensor_proto(batch, shape=(batch.shape)))
        start_time = datetime.datetime.now()
        result = stub.Predict(request, 10.0) # result includes a dictionary with all model outputs
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000
        processing_times = np.append(processing_times ,np.array([int(duration)]))
        output = tf_contrib_util.make_ndarray(result.outputs[model_spec['output_name']])

        print(f'Iteration {iteration}; '
              f'Processing time: {round(np.average(duration), 2):.2f} ms; '
              f'speed {round(1000 * batch_size / np.average(duration), 2):.2f} fps')

        if request_spec['imagenet'] == "True":
            print(f'\tImagenet top results in a single batch:')
            for i in range(output.shape[0]):
                single_result = output[[i],...]
                max_class = np.argmax(single_result)
                print(f'\t\t {i+1} image in batch: {classes.imagenet_classes[max_class]}')

    return output, processing_times, batch_size


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


def main():
    parser = argparse.ArgumentParser(
        description='Do requests to Tensorflow Serving using images or images in numpy format')
    parser.add_argument('--grpc_address', required=False, default='localhost',
                        help='Specify url to grpc service. Default: localhost')
    parser.add_argument('--grpc_port', required=False, default=9000,
                        help='Specify port to grpc service. Default: 9000')
    parser.add_argument('--input_name', required=False, default='import/input_tensor',
                        help='Specify input tensor name. Default: import/input_tensor')
    parser.add_argument('--output_name', required=False, default='import/softmax_tensor',
                        help='Specify output name. Default: import/softmax_tensor')
    parser.add_argument('--transpose_input', choices=["True", "False"], default="False",
                        help='Set to True to make NHWC->NCHW input transposing. Default: False',
                        dest='transpose_input')
    parser.add_argument('--batch_size', default=1,
                        help='Number of images in a single request. Default: 1',
                        dest='batch_size')
    parser.add_argument('--model_name', default='resnet',
                        help='Define model name, must be same as is in service. Default: resnet',
                        dest='model_name')
    parser.add_argument('--ssl', action='store_true', help="Enable SSL traffic")
    parser.add_argument('--performance', action='store_true',
                        help='Enable processing performance info')
    files = parser.add_mutually_exclusive_group(required=True)
    files.add_argument('--images_numpy_path', help='numpy in shape [n,w,h,c]')
    files.add_argument('--images_list', help='List of images in .jpg format')
    parser.add_argument('--image_size', default=224, help='Size of images. Default: 224')
    parser.add_argument('--imagenet', choices=["True", "False"], default="True",
                        help='Set to false for non-Imagenet datasets. Default: True')
    args = vars(parser.parse_args())

    endpoint_address = f'{args["grpc_address"]}:{args["grpc_port"]}'
    model_spec = dict()
    model_spec['model_name'] = args['model_name']
    model_spec['input_name'] = args['input_name']
    model_spec['output_name'] = args['output_name']
    request_spec = dict()
    request_spec['batch_size'] = args['batch_size']
    request_spec['transpose_input'] = args['transpose_input']
    request_spec['imagenet'] = args['imagenet']
    request_spec['performance'] = args['performance']
    request_spec['ssl'] = args['ssl']

    imgs = prepare_images(args)

    if request_spec['transpose_input'] == "True":
        imgs = imgs.transpose((0, 3, 1, 2))

    output, processing_times, batch_size = inference(
        model_spec, request_spec, endpoint_address, imgs)

    if request_spec['performance'] == "True":
        get_processing_performance(processing_times, batch_size)


if __name__ == "__main__":
    main()
