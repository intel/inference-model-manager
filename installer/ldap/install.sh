#!/bin/bash
. ../utils/messages.sh
cd $HELM_TEMP_DIR/ldap
header "Installing LDAP"
helm install --name imm-ldap -f values.yaml stable/openldap
show_result $? "LDAP installation succeded" "Failed to install LDAP"
cd -
