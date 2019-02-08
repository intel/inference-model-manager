# Troubleshooting

## Typical errors

### An error occurred during namespace creation: Unauthorized

```console
./api_call.sh create tenant
Create tenant
Please provide tenant name abbb
Please provide scope (group name) sun
{"title": "An error occurred during namespace creation: Unauthorized"}
```
Above error indicates on wrong connection information in kubeapi server config file, most probably wrong oidc issuer url or wrong port in issuer url.

### Connection aborted.', ConnectionRefusedError(111, 'Connection refused')'

```console
./api_call.sh create tenant
Create tenant
Please provide tenant name abbb
Please provide scope (group name) sun
{"title": "Unexpected error occurred: ('Connection aborted.', ConnectionRefusedError(111, 'Connection refused'))"}
```
Above message can indicate on Minio -- Management Api connections issues, credentials or wrong port included in minio-access-info kubernetes secret.

### Unexpected error occurred: Failed to parse: minioplatform.default:9000\n

```console
./api_call.sh create tenant
Create tenant
Please provide tenant name abbb
Please provide scope (group name) sun
{"title": "Unexpected error occurred: Failed to parse: minioplatform.default:9000\n"}
```
minio.endpoint_url variable in minio-access-info was base64 encoded with additional newline sign. 

### Unexpected error occurred: 'dict' object has no attribute 'to_dict'

```console
./api_call2.sh ls tenant
{"title": "Unexpected error occurred: 'dict' object has no attribute 'to_dict'"}

INFO:management_api.tenants.tenants:List tenants
ERROR:management_api.utils.errors_handling:Unexpected error occurred: 'dict' object has no attribute 'to_dict'
```
Minio -- Management Api connection problems, most probably wrong port number included in minio.endpoint_url in minio-access-info kubernetes secret.

### Unexpected error occurred: Could not connect to the endpoint URL: "http://minio.default:9000/mytenant?list-type=2"

Minio URL/service is not set correctly

### During installation of DEX - failed to initialize storage: failed to perform migrations: creating migration table: unable to open database file

Dex needs storage (for persistent state)



## Additional hints

### Install tiller on kubernetes cluster

```	
kubectl -n kube-system create serviceaccount tiller	
 kubectl create clusterrolebinding tiller \	
  --clusterrole cluster-admin \	
  --serviceaccount=kube-system:tiller	
 helm init --service-account tiller	
```

### How to configure helm on kubespray

Set flag `helm_enabled: true` in `inventory/<clustername>/k8s-cluster/addons.yml`
