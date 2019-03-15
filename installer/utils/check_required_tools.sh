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

tools=("ping" "unbuffer" "kops" "kubectl" "helm" "jq" "yq" "virtualenv" "python3.6" "bats")

missing=""
for cmd in "${tools[@]}"
do
   result=`command -v $cmd`
   if [ -z "$result" ]
   then
      missing="$missing $cmd "
   fi
done

if [ ! -z "$missing" ]
then
   failure "Please install tools: [$missing]"
   exit 1
fi

