#!/bin/bash
# Copyright (c) 2018-2019 Intel Corporation
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

# Generate a CA to be used for creating client certificates
openssl genrsa -out ca-cert-tf.key 4096
openssl req -new -x509 -days 365 -key ca-cert-tf.key -out ca-cert-tf.crt -subj "/CN=ca"
# Generate client key and certificate authorizing access to inference endpoints. Change the CN as needed.
openssl genrsa -out client-tf.key 4096
openssl req -new -key client-tf.key -out client-tf.csr -subj "/CN=client"
openssl x509 -req -days 365 -in client-tf.csr -CA ca-cert-tf.crt -CAkey ca-cert-tf.key -set_serial 01 -out client-tf.crt
echo 01 > /tmp/certserial
echo 01 > /tmp/crlnumber
touch /tmp/certindex
openssl ca -config ca.conf -gencrl -keyfile ca-cert-tf.key -cert ca-cert-tf.crt -out root.crl.pem
cat root.crl.pem >> ca-cert-tf.crt
if [[ "$OSTYPE" == "darwin"* ]]; then
    export CERT=`cat ca-cert-tf.crt|base64`
else
    export CERT=`cat ca-cert-tf.crt|base64 -w0`
fi
