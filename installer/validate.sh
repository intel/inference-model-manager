#!/bin/bash
DNS_DOMAIN_NAME="krzych2.nlpnp.adsdcsp.com"
cd validate
. test_dex_ldap.sh https://dex.$DNS_DOMAIN_NAME
cd ..

python3 webbrowser_authenticate.py --address mgt.krzych2.nlpnp.adsdcsp.com --proxy_host proxy-mu.intel.com --proxy_port 911 -k

