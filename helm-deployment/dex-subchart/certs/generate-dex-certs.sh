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

# This script shows how to generate certificates for dex internal interface

# Generate CA
openssl genrsa -out ca-dex.key 4096
openssl req -new -x509 -days 365 -key ca-dex.key -out ca-dex.crt -subj "/CN=ca-dex"

# Generate server key/cert
openssl genrsa -out dex.key 4096
openssl req -new -key dex.key -out dex.csr -subj "/CN=dex.${DEX_NAMESPACE}"
openssl x509 -req -days 365 -in dex.csr -CA ca-dex.crt -CAkey ca-dex.key -set_serial 01 -out dex.crt
