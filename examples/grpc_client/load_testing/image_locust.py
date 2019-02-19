import sys
import os
from locust import Locust, TaskSet, task, events
import datetime
import tensorflow.contrib.util as tf_contrib_util

sys.path.append(os.path.realpath(os.path.join(os.path.realpath(__file__), '../../')))  # noqa
from grpc_client_utils import prepare_certs, prepare_stub_and_request, MODEL_STATUS_REQUEST, \
    INFERENCE_REQUEST
from images_2_numpy import load_images_from_list
from grpc_client import get_stub_and_request


class MyTaskSet(TaskSet):
    data_for_requests = []
    GRPC_ADDRESS = os.environ.get('GRPC_ADDRESS', "URL")
    MODEL_NAME = os.environ.get('MODEL_NAME', "resnet")
    TENSOR_NAME = os.environ.get('TENSOR_NAME', "in")
    IMAGES = os.environ.get('IMAGES', None)
    SERVER_CERT = os.environ.get('SERVER_CERT', None)
    CLIENT_CERT = os.environ.get('CLIENT_CERT', None)
    CLIENT_KEY = os.environ.get('CLIENT_KEY', None)
    TRANSPOSE = bool(os.environ.get('TRANSPOSE', False))
    TIMEOUT = float(os.environ.get('TIMEOUT', 10))
    stub = None
    request = None
    imgs = None

    def on_start(self):
        if self.GRPC_ADDRESS in 'URL':
            print("Url to service is not set")
            sys.exit(0)
        if self.IMAGES is not None:
            images = self.IMAGES.split(',')
            self.imgs = load_images_from_list(images, 224, len(images))
        if self.TRANSPOSE:
            self.imgs = self.imgs.transpose((0, 3, 1, 2))
        certs = dict()
        certs['server_cert'] = self.SERVER_CERT
        certs['client_cert'] = self.CLIENT_CERT
        certs['client_key'] = self.CLIENT_KEY
        self.stub, self.request = get_stub_and_request(self.GRPC_ADDRESS, self.MODEL_NAME, certs, True, None,
                                             INFERENCE_REQUEST)
        self.request.inputs[self.TENSOR_NAME].CopyFrom(tf_contrib_util.make_tensor_proto(self.imgs, shape=(self.imgs.shape)))

    def on_stop(self):
        print("Tasks was stopped")

    @task
    def my_task(self):
        start_time = datetime.datetime.now()
        try:
            result = self.stub.Predict(self.request, self.TIMEOUT)
        except Exception as e:
            end_time = datetime.datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000
            events.request_failure.fire(request_type="grpc", name='grpc', response_time=duration, exception=e)
        else:
            end_time = datetime.datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000
            events.request_success.fire(request_type="grpc", name='grpc', response_time=duration, response_length=0)


class MyLocust(Locust):
    task_set = MyTaskSet
    min_wait = 0
    max_wait = 0

    def teardown(self):
        print("Locust ends his tasks")
