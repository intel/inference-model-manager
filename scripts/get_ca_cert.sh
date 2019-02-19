MGT_API=$1
if [ ! -z "$HTTP_PROXY" ]; then
proxytunnel -p proxy-chain.intel.com:912 -d $MGT_API:443 -a 7000 &
openssl s_client -connect localhost:7000 -servername $MGT_API -showcerts  < /dev/null 2>/dev/null | grep "s:/CN=ca-ing" -A 100| openssl x509 -outform pem
killall "proxytunnel: [daemon]"
else
openssl s_client -connect $MGT_API:443 -servername $MGT_API -showcerts  < /dev/null 2>/dev/null | openssl x509 -outform pem
fi
