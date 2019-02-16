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

# Example how to create self-signed CA for Management API external interface


# Generate server key/cert
openssl genrsa -out ing-mgt-api.key 4096
openssl req -new -key ing-mgt-api.key -out ing-mgt-api.csr -subj "/CN=${MGMT_DOMAIN_NAME}"
openssl x509 -req -days 365 -in ing-mgt-api.csr -CA ca-ing.crt -CAkey ca-ing.key -set_serial 01 -out ing-mgt-api.crt
cat ca-ing.crt >> ing-mgt-api.crt
