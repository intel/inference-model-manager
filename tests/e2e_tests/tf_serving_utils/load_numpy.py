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
import sys
import os
import numpy
sys.path.append(os.path.realpath(os.path.join(os.path.realpath(__file__), '../../../../examples/grpc_client')))  # noqa
from images_2_numpy import get_jpeg

IMAGES = numpy.load("e2e_tests/tf_serving_utils/images.npy")[:2]
LABELS = [277, 210]

JPG_IMAGE = get_jpeg("e2e_tests/tf_serving_utils/fox.jpg", 224)
