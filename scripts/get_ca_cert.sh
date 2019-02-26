
MGT_API=$1
PROXY=$2
if [ ! -z "$PROXY" ]; then
    proxytunnel -p $PROXY -d $MGT_API:443 -a 7000 &
    openssl s_client -connect localhost:7000 -servername $MGT_API -showcerts  < /dev/null 2>/dev/null |grep "s:.*CN.*ca-ing" -A 100 | openssl x509 -outform pem
    kill `ps -ef | grep proxytunnel | awk '{print $2}'`
else
    openssl s_client -connect $MGT_API:443 -servername $MGT_API -showcerts  < /dev/null 2>/dev/null | grep "s:.*CN.*ca-ing" -A 100|  openssl x509 -outform pem
fi
