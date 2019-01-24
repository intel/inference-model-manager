# Management API

Management API component provides a convenience layer for controlling CRD records and handling AI models in Minio storage.
With that users and platform admin can control all aspects of Inference Endpoints functionality without direct access
to Kubernetes API. 

Authorization of the models management functions is implemented based on user token permissions in kubernetes namespace 
associated with the Minio bucket.
 
All the kubernetes operations are executed by Management API component using the user token so the authorization 
is configured in Kubernetes using appropriate user roles and role bindings. 

The roles and permissions are created automatically by Management API during tenant creation. 


## Docker image building

```
make docker_build
```
While the docker image is built it should be pushed to a docker registry accessible by the K8S cluster.

## Deployment in Kubernetes cluster

Refer to the [helm chart](../helm-deployment/management-api-subchart) documentation. 


## API documentation

### Tenants
Tenants are managed by Platform Admin. It is possible to take actions as follow:
* create tenant,
* delete tenant,
* list tenants.

#### Create tenant

Call a POST operation on `https://<management-api-address>/tenants`:
```
curl -X POST "https://<management_api_address>/tenants" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"name\": <string>, \"cert\": <cert_encoded_with_base64>, \"scope\": <string>, \"quota\": {}}"
```

When an operation ends with success, it returns a statement (example for a tenant with a name `test`):

```Tenant test created```

#### Quota configuration for tenant

Call a POST operation on `https://<management-api-address>/tenants` with quota defined:
```
curl -X POST https://<management-api-address>/tenants -H “accept: application/json” \
H “Authorization: <id-token>” H “Content-Type: application/json” d {\”name\”: <string>, \ 
\”cert\”: <cert_encoded_with_base64>\”, \”scope\”: <string>, \
\”quota\”: {\”maxEndpoints\”: <int>, \”requests.cpu\”: <string>, \”limits.cpu\”: <string>, \ 
\”requests.memory\”: <string>, \”limits.memory\”: <string>}}
```

Quota parameter is required, but there is an option to pass an empty dictionary instead of resource specification
(see Create tenant).

#### List tenants

Call a GET operation on `https://<management-api-address>/tenants`:
```
curl -X GET "https://<management_api_address>/tenants" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json"
```

When an operation ends with success, it returns a statement (example for a tenant with a name `test`):
 
```Tenants present of platform: test```


#### Delete tenant

Call a DELETE operation on `https://<management-api-address>/tenants`:
```
curl -X DELETE "https://<management_api_address>/tenants" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json" -d "{\"name\": <string>}"
```

When an operation ends with success, it returns a statement (example for a tenant with a name `test`):
 
```Tenant test deleted```

##
### Models 
Models are pretrained deep learning models able to be served via Tensoflow Serving.

#### Upload model
To upload model use `scripts/model_upload_cli.py`.  
Run help to get information about usage:
```
python model_upload_cli.py -h
```

#### List models
Call a GET operation on `https://<management-api-address>/tenants/<tenant-name>/models`:

```
curl -X GET "https://<management_api_address>/tenants/<tenant-name>/models" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json" }"
```

When an operation ends with success, it returns a statement (example for a tenant `test`):
```
Models in test tenant (model name, model version, model size, deployed count): 
[('resnet', '1', 102619858, 0), ('resnet', '2', 102619858, 0)]
```

#### Delete model
Call a DELETE operation on `https://<management-api-address>/tenants/<tenant-name>/models`:
```
curl -X DELETE "https://<management_api_address>/tenants/<tenant-name>/models" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"modelName\": <string>, \"modelVersion\": <int>}"
```
When an operation ends with success, it returns a statement (example for a model `resnet` in version 1):
```
Model deleted: resnet-1
```

##
### Endpoints
Endpoints are managed by Platform Users. It is possible to take actions as follow:
* create endpoint
* view endpoint
* update endpoint
* scale endpoint
* delete endpoint
* list endpoints

#### Model version policy
In order to specify particular model versions to be served, provide `modelVersionPolicy` parameter
 while creating or updating endpoint. `modelVersionPolicy` parameter is a string limited to:
 * `{ latest {} }` - only latest version of the model will be served,
 * `{ all {} }` - all available versions of the model will be served,
 * `{ specific { versions: 1 versions: 2 ... }` - specified versions of the model will be
  served 
  
If `modelVersionPolicy` parameter was not provided during endpoint creation, default 
  value is 
`{latest {}}`.

#### Create endpoint
Call a POST operation on `https://<management-api-address>/tenants/<tenant-name>/endpoints`:
```
curl -X POST "https://<management_api_address>/tenants/<tenant-name>/endpoints" -H "accept: 
application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"endpointName\": <string>, \"modelName\": <string>, \"modelVersionPolicy\": <string>, 
\"servingName\": <string>,
 \"subjectName\": <string>, \"resources\": <dict>}"
```

When an operation ends with success, it returns a statement (example for an endpoint with a name 
`endpoint` in a `test` tenant with a `test-domain.com` domain):
```
Endpoint created:
{‘url’: ‘endpoint-test.test-domain.com:443’}
```

#### List endpoints
Call a GET operation on `https://<management-api-address>/tenants/<tenant-name>/endpoints`:
```
curl -X GET "https://<management_api_address>/tenants/<tenant-name>/endpoints" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json"
```

When an operation ends with success, it returns a statement (example for endpoins `endpoint1` and 
`endpoint2` in a `test` tenant with a `test-domain` domain):
```
Endpoints present in test tenant: 
[{'name': 'endpoint1', 'url': 'endpoint1-test.test-domain.com:443', 'status': 'Available'}, 
{'name': 'endpoint2', 'url': 'endpoint2-test.test-domain.com:443', 'status': 'Available'}]
```

#### Delete endpoint
Call a DELETE operation on `https://<management-api-address>/tenants/<tenant-name>/endpoints`:
```
curl -X DELETE "https://<management_api_address>/tenants/<tenant-name>/endpoints" \
-H "accept: application/json" -H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"endpointName\": <string>}"
``` 

When an operation ends with success, it returns a statement (example for an `endpoint` with a name `test`):
```
Endpoint test deleted
```

#### View endpoint
Call a GET operation on 
`https://<management-api-address>/tenants/<tenant-name>/endpoints/<endpoint-name>`:
```
curl -X GET "https://<management_api_address>/tenants/<tenant-name>/endpoints/<endpoint-name>" \
-H "accept: application/json" -H "Authorization: <jwt_token>" -H "Content-Type: application/json"
```

When an operation ends with success, it returns a statement (example for an endpoint with a name 
`test-endpoint` from `test` tenant):
```
Endpoint test-endpoint in test tenant: 
{'Endpoint status': {'Running pods': 1, 'Pending pods': 0, 'Failed pods': 0}, 
'Model path': {'url': 'endpoint-test.example-domain.com:443'}, 'Subject name': 'client', 
'Resources': {'limits': {'cpu': '2', 'memory': '2Gi'}, 'requests': {'cpu': '1', 'memory': '1Gi'}}, 
'Replicas': {'Available': 1, 'Unavailable': None}}
```

#### Update endpoint
Call a PATCH operation on `https://<management-api-address>/tenants/<tenant-name>/endpoints/<endpoint-name>:`

```
curl -X PATCH "https://<management_api_address>/tenants/<tenant-name>/endpoints/<endpoint-name>" \
-H "accept: application/json" -H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"modelName\": <string>, \"modelVersionPolicy\": <string>}"
```
When an operation ends with success, it returns a statement (example for an endpoint with a name 
`endpoint` from `test`):
```
Endpoint {'url': 'endpoint-test.example-domain.com:443'} patched successfully. 
New values: {'modelName': 'new-model', 'modelVersionPolicy': '{latest {}}'}
```

#### Scale endpoint

Call a PATCH operation on `https://<management-api-address>/tenants/<tenant-name>/endpoints/<endpoint-name>/replicas`:

```
curl -X PATCH "https://<management_api_address>/tenants/<tenant-name>/endpoints/<endpoint-name>/replicas" \
-H "accept: application/json" -H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"replicas\": <int>}"
```
When an operation ends with success, it returns a statement (example for an endpoint with a name 
`endpoint` from `test`):
```
Endpoint {'url': 'endpoint-test.example-domain.com:443'} patched successfully. New values: {'replicas': 2}
```

### Servings

#### List servings
Call a GET operation on `https://<management-api-address>/servings`:
```
curl -X GET "https://<management_api_address>/servings" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json"
```

When an operation ends with success, it returns a statement (example for a two default serving templates):
```
Servings in crd: ['ovms', 'tf-serving']
```

#### Get serving
Call a GET operation on `https://<management-api-address>/servings/<serving-name>`:

```
curl -X GET "https://<management_api_address>/servings/<serving_name>" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json"
```

When an operation ends with success, it returns a statement (example for a `tf-serving`):
```
Serving template tf-serving: 
<configMap.tmpl: <yaml template> deployment.tmpl: <yaml template> ingress.tmpl: <yaml template>
service.tmpl: <yaml tmeplate>
```

## Script for API calls

You can refer to `imm` example CLI employing all API endpoints on [scripts](../scripts/)
