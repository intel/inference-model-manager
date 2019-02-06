#!/bin/bash
. ../utils/fill_template.sh
. ../utils/messages.sh

header "Installation of CRD Controller"
cd ../../helm-deployment/crd-subchart
fill_template "<dns_domain_name>" $DOMAIN_NAME values.yaml
helm install .
show_results $? "CRD installation completed" "Failed to install CRD"
cd -
