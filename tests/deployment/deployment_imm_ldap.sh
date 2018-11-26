#!/usr/bin/env bash
helm install --name imm-ldap -f ldap/values.yaml stable/openldap
