#!/bin/bash
. ../utils/fill_template.sh
. ../utils/messages.sh

header "Installation of CRD Controller"
DOMAIN_NAME=$1
cd $HELM_TEMP_DIR/crd-subchart
fill_template "<dns_domain_name>" $DOMAIN_NAME values.yaml
helm install .
show_result $? "CRD installation completed" "Failed to install CRD"
cd -
