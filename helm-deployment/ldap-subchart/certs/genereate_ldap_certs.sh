#!/bin/bash
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

# Example how to create self-signed CA for Management API external interface

# Generate CA for Management Api
openssl genrsa -out ca-ldap.key 4096
openssl req -new -x509 -days 365 -key ca-ldap.key -out ca.crt -subj "/CN=ca-ldap"

# Generate server key/cert
openssl genrsa -out ldap.key 4096
openssl req -new -key ldap.key -out ldap.csr -subj "/CN=imm-openldap.default"
openssl x509 -req -days 365 -in ldap.csr -CA ca.crt -CAkey ca-ldap.key -set_serial 01 -out ldap.crt