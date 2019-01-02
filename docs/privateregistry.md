## Private Docker Registry
Private Docker Registry used to store Management Api and Server Controller images requires creation of special kubernetes secret.

Example secret creation, Google Cloud Registry assumed:
```
kubectl create secret docker-registry gcr-json-key \
--docker-server=https://gcr.io \
--docker-username=_json_key \
--docker-password="$(cat ~/<key file name>.json)" \
--docker-email=email@example.com
```
Patch service account used for imagePullSecret option for Management Api and Server Controller.

```
kubectl patch serviceaccount mgt-api \
 -p "{\"imagePullSecrets\": [{\"name\": \"gcr-json-key\"}]}" \
-n mgt-api
```
```
kubectl patch serviceaccount server-controller \
 -p "{\"imagePullSecrets\": [{\"name\": \"gcr-json-key\"}]}" \
-n crd
```
