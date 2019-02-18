#!/bin/bash
params=("CLUSTER_NAME" "DNS_DOMAIN_NAME")

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
   echo "Variables $empty must be set before starting installation"
   exit 1
fi

