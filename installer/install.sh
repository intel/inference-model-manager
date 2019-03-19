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

. utils/show_help.sh

export B64DECODE="base64 --decode"
export B64ENCODE="base64 -w0"
export SED_CMD="sed"
if [[ "$OSTYPE" == "darwin"* ]]; then     
   export SED_CMD="gsed"
   export B64ENCODE="base64"
fi

. utils/check_required_tools.sh

OPTIND=1 
kops_env=""
domain=""
gce_zone="us-west1"
quiet="no"

while getopts "h?qsk:d:z:g:p:A:S:t" opt; do
    case "$opt" in
    h|\?)
        show_help
        exit 0
        ;;
    q)  quiet="yes"
        ;;
    k)  kops_env=$OPTARG
        ;;
    d)  domain=$OPTARG
        ;;
    z)  gce_zone=$OPTARG
        ;;      
    s)  export SKIP_K8S_INSTALLATION="true"
        ;;
    g)  export GCE_USER=$OPTARG
        ;;
    p)  export PROXY=$OPTARG
        ;;
    A)  export MINIO_ACCESS_KEY=$OPTARG
        ;;
    S)  export MINIO_SECRET_KEY=$OPTARG
        ;;
    t)  export MGT_API_AUTHORIZATION="true"
        export DEFAULT_TENANT_NAME="default-tenant"
        ;;
    esac
done

shift $((OPTIND-1))


FILTER_CMD="cat"
if [[ "$quiet" == "yes" ]]; then
    echo "Enabling quiet mode"
    FILTER_CMD="grep --color=none '[[:cntrl:]]'"
fi

unbuffer ./main.sh "$kops_env" "$domain" "$gce_zone" 2>&1 | tee install.log | ${FILTER_CMD}

