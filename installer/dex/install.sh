#!/bin/bash
. ../utils/fill_template.sh
. ../utils/messages.sh

export ISSUER=$1
export DEX_NAMESPACE=$2
export DEX_DOMAIN_NAME=$3
header "Generating certificates for DEX"
cd $HELM_TEMP_DIR/dex-subchart/certs
./generate-ing-ca.sh
./generate-dex-certs.sh 
./generate-ing-dex-certs.sh
cd -

header "Installing DEX"
cp dex_config_tmpl.yaml dex_config.yaml
fill_template "toreplacedbyissuer" $ISSUER dex_config.yaml
export OPENLDAP_SVC=`kubectl get svc|grep "openldap   "| awk '{ print $1 }'`
export OPENLDAP_SVC_ADDRESS="$OPENLDAP_SVC.default:389"
fill_template "toreplacebyldapaddress" $OPENLDAP_SVC_ADDRESS dex_config.yaml
helm install -f dex_config.yaml --set issuer=${ISSUER} --set ingress.hosts=${DEX_DOMAIN_NAME} --set ingress.tls.hosts=${DEX_DOMAIN_NAME} $HELM_TEMP_DIR/dex-subchart/
show_result $? "DEX installation succesful" "Failed to install DEX"
