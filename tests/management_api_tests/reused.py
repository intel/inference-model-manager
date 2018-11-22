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

from management_api_tests.config import PORTABLE_SECRETS_PATHS


def transform_quota(quota):
    transformed = {}
    for k, v in quota.items():
        keys = k.split('.')
        if len(keys) == 1:
            continue
        transformed.setdefault(keys[0], {})[keys[1]] = v
    return transformed


def propagate_secret(api_instance, source_secret_path, target_namespace):
    source_secret_namespace, source_secret_name = source_secret_path.split('/')
    source_secret = api_instance.read_namespaced_secret(
        source_secret_name, source_secret_namespace)

    source_secret.metadata.namespace = target_namespace
    source_secret.metadata.resource_version = None

    api_instance.create_namespaced_secret(namespace=target_namespace,
                                          body=source_secret)


def propagate_portable_secrets(api_instance, target_namespace):
    for portable_secret_path in PORTABLE_SECRETS_PATHS:
        propagate_secret(api_instance, portable_secret_path, target_namespace)
