#!/bin/bash
#
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

show_help() {
cat << EOF
Usage: 
${0##*/} [-h?qskdz]
Required optons:
    -k - cluster name
    -d - domain name
Additional options
    -z - GCE cluster zone (if using kops and GCE)
    -q - silent mode (shows only important logs)
    -s - skip cluster creation via kops
    -p - set proxy (address:port)
    -t - single tenant mode
    -A - set minio access key
    -S - set minio secret key
    -U - set URL to minio (if this parameter is set, minio chart will not be deploy)
    -V - set signature version for minio (default: s3v4)
    -R - set region for minio (default: us-east-1)
    -h/? - show help
Usage examples  
    ${0##*/} -k <name> -d <domain>
    ${0##*/} -k <name> -d <domain> -z <gce_zone>
    ${0##*/} -k <name> -d <domain> -s -q
    ${0##*/} -k <name> -d <domain> -s -q -p myproxy.com:911 -A minio_access_key -S minio_secret_key
    ${0##*/} -d <domain> -s -q -A minio_access_key -S minio_secret_key -U url_to_minio -R us-west-2
EOF
}
