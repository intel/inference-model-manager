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
openssl genrsa -out ca-ing-dex.key 4096
openssl req -new -x509 -days 365 -key ca-ing-dex.key -out ca-ing-dex.crt -subj "/CN=dex.cluster"

# Generate server key/cert
openssl genrsa -out ing-dex.key 4096
openssl req -new -key ing-dex.key -out ing-dex.csr -subj "/CN=dex"
openssl x509 -req -days 365 -in ing-dex.csr -CA ca-ing-dex.crt -CAkey ca-ing-dex.key -set_serial 01 -out ing-dex.crt
