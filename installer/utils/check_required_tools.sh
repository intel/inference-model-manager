#!/bin/bash
tools=("ping" "unbuffer" "kops" "kubectl" "helm" "jq" "yq" "virtualenv" "python3.6")

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
   echo "Please install tools: [$missing]"
   exit 1
fi

