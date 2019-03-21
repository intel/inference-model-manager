kubectl get secret ca-ing -n dex -o json | jq '.data."ca.crt"' | tr -d '"' | base64 --decode
