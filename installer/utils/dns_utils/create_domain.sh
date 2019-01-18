#sed -i "s/0.0.0.0/35.233.148.9/g" route_record.json
#sed -i "s/toreplacebydomainname/krzych.nlpnp.adsdcsp.com/g" route_record.json
cat route_record.json
#virtualenv .venvaws -p python3
. .venvaws/bin/activate
#pip install awscli --upgrade 
aws route53 change-resource-record-sets --hosted-zone-id Z11DOV0M5AJEBB --change-batch file://./route_record.json
deactivate

