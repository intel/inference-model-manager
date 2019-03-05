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
#!/bin/bash

function wait_for_kubectl() {
  seconds=$1 
  steps=$(($seconds/5))      
  for (( i = $steps; $i > 0; i=$i -1)); do
       ready=`kubectl get pods -n not_existing_namespace --request-timeout=5s 2>&1|grep "No resources"`
       if [ ! -z "$ready" ]
       then
         echo "Kubectl command available"
         return 
       fi
       sleep 1
       echo -ne "\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r $i seconds left" 
  done
  echo "Could not get working kubectl during time:  $seconds s, aborting "
  exit 1
}

