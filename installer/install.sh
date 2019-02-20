#!/bin/bash
. utils/show_help.sh
. utils/check_required_tools.sh

OPTIND=1 
kops_env=""
domain=""
gce_zone="us-west1"
quiet="no"

while getopts "h?qsk:d:z:g:p" opt; do
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
    s)  export SKIP_K8S_INSTALLATION="True"
        ;;
    g) export GCE_USER=$OPTARG
	;;
    p) export PROXY="Proxy"
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

unbuffer ./main.sh "$kops_env" "$domain" "$gce_zone" 2>&1 | tee install.log | ${FILTER_CMD}

