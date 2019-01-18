#!/bin/bash

OPTIND=1 
kops_env=""
domain=""
quiet="no"

while getopts "h?qk:d:" opt; do
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
    esac
done

shift $((OPTIND-1))

export B64DECODE="base64 -D"
export SED_CMD="sed"

if [[ "$OSTYPE" == "darwin"* ]]; then     
   brew install gnu-sed      
   brew install expect
   export SED_CMD="gsed"
fi

FILTER_CMD="cat"
if [[ "$quiet" == "yes" ]]; then
echo "Enabling quiet mode"
FILTER_CMD="grep --color=none '[[:cntrl:]]'"
fi

unbuffer ./main.sh $kops_env $domain 2>&1 | tee install.log | ${FILTER_CMD}

