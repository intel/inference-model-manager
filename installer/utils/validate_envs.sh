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

# import from the same directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
. $DIR/messages.sh

params=("DNS_DOMAIN_NAME")

empty=""
for var in "${params[@]}"
do
   if [ -z "${!var}" ]
   then
      empty="$empty $var "
   fi
done

if [ ! -z "$empty" ]
then
   failure "Variables $empty must be set before starting installation"
   exit 1
fi

