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

# How to generate certificates for Management API internal interface

# Generate CA for Management Api
openssl genrsa -out ca-mgt-api.key 4096
openssl req -new -x509 -days 365 -key ca-mgt-api.key -out ca-mgt-api.crt -subj "/CN=ca-mgt-api"

# Generate server key/cert
openssl genrsa -out mgt-api.key 4096
openssl req -new -key mgt-api.key -out mgt-api.csr -subj "/CN=management-api.${MGT_NAMESPACE}"
openssl x509 -req -days 365 -in mgt-api.csr -CA ca-mgt-api.crt -CAkey ca-mgt-api.key -set_serial 01 -out mgt-api.crt
