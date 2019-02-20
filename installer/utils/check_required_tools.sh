#!/bin/bash
tools=("unbuffer" "kops" "helm" "jq" "yq" "virtualenv" "python3.6")

missing=""
for cmd in "${tools[@]}"
do
   result=`command -v $cmd`
   if [ -z "$result" ]
   then
      missing="$empty $cmd "
   fi
done

if [ ! -z "$missing" ]
then
   echo "Please install tools: [$missing]"
   exit 1
fi

