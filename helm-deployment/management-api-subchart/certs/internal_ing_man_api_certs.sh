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

# This script shows how to generate test keys and certs

# Generate CA
openssl genrsa -out ca-ing-man-api.key 4096
openssl req -new -x509 -days 365 -key ca-ing-man-api.key -out ca-ing-man-api.crt -subj "/CN=management-api.cluster"

# Generate server key/cert
openssl genrsa -out ing-man-api-server.key 4096
openssl req -new -key ing-man-api-server.key -out ing-man-api-server.csr -subj "/CN=management-api.cluster"
openssl x509 -req -days 365 -in ing-man-api-server.csr -CA ca-ing-man-api.crt -CAkey ca-ing-man-api.key -set_serial 01 -out ing-man-api-server.crt
