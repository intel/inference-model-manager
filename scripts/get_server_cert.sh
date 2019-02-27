ENDPOINT_ADDRESS=$1
PROXY=$2
if [ ! -z "$PROXY" ]; then
    proxytunnel -p $PROXY -d $ENDPOINT_ADDRESS:443 -a 7000 &
    openssl s_client -connect localhost:7000 -servername $ENDPOINT_ADDRESS -showcerts  < /dev/null 2>/dev/null |grep "s:.*CN.*${DOMAIN_NAME}" -A 100 | openssl x509 -outform pem
    kill `ps -ef | grep proxytunnel | awk '{print $2}'`
else
    openssl s_client -connect $ENDPOINT_ADDRESS:443 -servername $ENDPOINT_ADDRESS -showcerts  < /dev/null 2>/dev/null | grep "s:.*CN.*${DOMAIN_NAME}" -A 100|  openssl x509 -outform pem
fi
