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

TENANT_NAME = os.environ.get('E2E_TENANT_NAME', 'test')
MODEL_NAME = os.environ.get('E2E_MODEL_NAME', 'e2emodel')
ENDPOINT_NAME = os.environ.get('E2E_ENDPOINT_NAME', MODEL_NAME + 'endpoint')
CREATE_ENDPOINT_VP = '{specific {versions: 1}}'
UPDATE_ENDPOINT_VP = '{specific {versions: 2}}'
