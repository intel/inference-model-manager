# Platform admin guide

## Creating new tenants

Tenants can be managed by using a REST endpoint exposed by Management API with an address:
 
`https://<management-api-address>/tenants`
 
It this section explains possible operations with this endpoint.
 
All operations presented in this document require that user is logged in to platform and has aquired JTW token from
oauth2 server (dex). The token is stored in a config file `.imm`. The user needs to belong to the platform admin group
set during Management API component deployment. 

Login operation is based on Oauth2 process. It can be implemented using [example CLI script](../scripts) 
 
Each tenant is using a dedicated Kubernetes namespace and a bucket in Minio storage.

To create a tenant it is needed to provide the following parameters:
- Tenant name
- CA certificate which is used to sign gRPC authorization client certificates. It will be stored in K8S secret 
‘ca-cert-secret’ in the tenant namespace. Certificate should be decoded by base64
- scope name which represents a group in JWT token
- quota – see Quota configuration for tenants.

After successful operation there are created the following resources:
- new K8S namespace
- a set of K8S secret records storing required credentials and TLS certificates 
- K8S role binding for the defined users group from IdP
- Minio bucket with the same name like the tenent and the namespace 


Check for the API example on [Management API doc](../management) and review [example CLI](../scripts).


## Quota configuration for tenants

It is possible to create tenant with a limited CPU and memory resource allocation. 
Management API can set the quota values in K8S so the same parameters are supported:  
- cpu
- requests.cpu
- limits.cpu
- memory
- requests.memory
- limits.memory

All these values are compared with one regex pattern:
 
`^([+]?[0-9.]+)([eEinumkKMGTP]*[+]?[0-9]*)$`

Learn more about namespace quotas in 
[K8S documentation](https://kubernetes.io/docs/concepts/policy/resource-quotas/#compute-resource-quota) 
and managing compute resources (https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/).  	
 
 
Additionally, it is possible to specify how many endpoints can be created within a tenant. 
To do that, use a parameter `maxEndpoints`.

All the quota parameters are optional.
 
Check for the API example on [Management API doc](../management) and review [example CLI](../scripts).


## Listing tenants

Platform admin can list names of tenants by using GET API request on `https://<management-api-address>/tenants` address.

Check for the API example on [Management API doc](../management) and review [example CLI](../scripts).


## Deleting a tenant

*WARNING*

Deleting tenants is irreversible.

It removes all the K8S records associated with the tenant namespace and drop the tenamt Minio bucket. 

Check for the API example on [Management API doc](../management) and review [example CLI](../scripts).
