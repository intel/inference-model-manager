OP=$1 # CREATE, UPSERT, DELETE
IP_ADDR=$2
DOMAIN=$3
SED_CMD=sed
if [ "$(uname)" == "Darwin" ]; then
        SED_CMD=gsed
fi   

cp route_record_tmpl.json route_record.json
$SED_CMD -i "s/<operation>/$OP/g" route_record.json
$SED_CMD -i "s/<ip_address>/$IP_ADDR/g" route_record.json
$SED_CMD -i "s/<dns_domain_name>/$DOMAIN/g" route_record.json
echo "Created Route53 config:"
cat route_record.json
rm -fr .venvaws
virtualenv .venvaws -p python3
. .venvaws/bin/activate
pip install awscli --upgrade 
aws route53 change-resource-record-sets --hosted-zone-id Z11DOV0M5AJEBB --change-batch file://./route_record.json
deactivate

