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

