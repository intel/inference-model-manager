MGT_API=$1
USE_PROXY=$2
if [ ! -z "$USE_PROXY" ]; then
echo "Starting proxytunnel"
proxytunnel -p proxy-chain.intel.com:912 -d $MGT_API:443 -a 7000 &
openssl s_client -connect localhost:7000 -servername $MGT_API -showcerts  < /dev/null 2>/dev/null | grep "CN" -A 100 | grep "ca-ing" -A 100| openssl x509 -outform pem
kill `ps -ef | grep proxytunnel | awk '{print $2}'`
else
openssl s_client -connect $MGT_API:443 -servername $MGT_API -showcerts  < /dev/null 2>/dev/null | grep "CN" -A 100 |grep "ca-ing" -A 100|  openssl x509 -outform pem
fi
