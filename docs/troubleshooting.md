# Troubleshooting

## Typical errors

An error occurred during namespace creation: Unauthorized

```console
./api_call.sh c t
Create tenant
Please provide tenant name abbb
Please provide scope (group name) sun
{"title": "An error occurred during namespace creation: Unauthorized"}
```
Above error indicates on wrong connection information in kubeapi server config file, most probably wrong oidc issuer url or wrong port in issuer url.

Connection aborted.', ConnectionRefusedError(111, 'Connection refused')'

```console
./api_call.sh create t
Create tenant
Please provide tenant name abbb
Please provide scope (group name) sun
{"title": "Unexpected error occurred: ('Connection aborted.', ConnectionRefusedError(111, 'Connection refused'))"}
```
Above message can indicate on MinIO -- Management Api connections issues, credentials or wrong port included in minio-access-info kubernetes secret.

Unexpected error occurred: Failed to parse: minioplatform.defaul:9000\n

```console
./api_call.sh c t
Create tenant
Please provide tenant name abbb
Please provide scope (group name) sun
{"title": "Unexpected error occurred: Failed to parse: minioplatform.defaul:9000\n"}
```
minio.endpoint_url variable in minio-access-info was base64 encoded with additional newline sign. 

Unexpected error occurred: 'dict' object has no attribute 'to_dict'

```console
./api_call2.sh ls t
{"title": "Unexpected error occurred: 'dict' object has no attribute 'to_dict'"}

INFO:management_api.tenants.tenants:List tenants
ERROR:management_api.utils.errors_handling:Unexpected error occurred: 'dict' object has no attribute 'to_dict'
```
MinIO -- Management Api connection problems, most probably wrong port number included in minio.endpoint_url in minio-access-info kubernetes secret.

## Hints
Changes required by switching from Load Balancer to Node Port

Replace default 443 port in $ISSUER variable (tests/deployment/dex_config.yaml and tests/deployment/deployment_dex.sh) before running dex deployment with node port.

```
kubectl get svc -n ingress-nginx
NAME                   TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                      AGE
default-http-backend   ClusterIP                   <none>        80/TCP                       
ingress-nginx          NodePort                    <none>        80:31641/TCP,443:30258/TCP   
```
Node port used for https connection can be found next to ingress-nginx kubernetes service.
Add port number to KubeApi server connection to Dex details oidc issuer url.

Private Docker Registry:
Create secret docker-registry
Example secret creation, Google Cloud Registry assumed: 
```
kubectl create secret docker-registry gcr-json-key \
--docker-server=https://gcr.io \
--docker-username=_json_key \
--docker-password="$(cat ~/<key file name>.json)" \
--docker-email=email@example.com
```
Patch service account used for imagePullSecret option:

```
kubectl patch serviceaccount server-controller \
 -p "{\"imagePullSecrets\": [{\"name\": \"gcr-json-key\"}]}"
-n mgt-api
```
```
kubectl patch serviceaccount server-controller \
 -p "{\"imagePullSecrets\": [{\"name\": \"gcr-json-key\"}]}"
-n crd
```


