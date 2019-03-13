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

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
. $DIR/messages.sh

function wait_for_pod() {
  seconds=$1      
  pod_prefix=$2
  namespace=$3
  for (( i = $seconds; $i > 0; i=$i -1)); do
       ready=`kubectl get pods -n $namespace|grep $pod_prefix|grep "Running"|grep -v "0/"`
       if [ ! -z "$ready" ]
       then
         return 
       fi
       sleep 1
       print_ne "\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r $i seconds left" 
  done
  failure "Could not found pod with prefix: $pod_prefix, aborting"
  exit 1
}

