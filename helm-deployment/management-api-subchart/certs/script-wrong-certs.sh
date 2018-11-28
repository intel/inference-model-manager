#!/bin/bash
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

# Generate invalid client certificate with improper subject name, but signed by proper CA (test purposes)
openssl genrsa -out bad-client.key 4096
openssl req -new -key bad-client.key -out bad-client.csr -subj "/CN=bad-client"
openssl x509 -req -days 365 -in bad-client.csr -CA ca-cert-tf.crt -CAkey ca-cert-tf.key -set_serial 01 -out bad-client.crt
