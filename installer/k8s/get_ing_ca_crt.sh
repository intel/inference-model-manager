kubectl get secret ca-ing -n default -o yaml|grep ca.crt|awk '{ print $2 }'|base64 --decode
