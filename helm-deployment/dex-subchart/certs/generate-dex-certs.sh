#!/usr/bin/env bash
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

# Script to generate valid certs for dex

# Generate valid CA for dex
openssl genrsa -out dex-ca.key 4096
openssl req -new -x509 -days 365 -key dex-ca.key -out dex-ca.crt -subj "/CN=ca-dex"

# Generate valid dex server key/cert
openssl genrsa -out dex.key 4096
openssl req -new -key dex.key -out dex.csr -subj "/CN=${DEX_DOMAIN_NAME}"
openssl x509 -req -days 365 -in dex.csr -CA dex-ca.crt -CAkey dex-ca.key -set_serial 01 -out dex.crt
