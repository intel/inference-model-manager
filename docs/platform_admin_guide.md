# Platform admin guide

Tenants can be managed by using a REST endpoint exposed by Management API with an address:

`https://<management-api-address>/tenants`

## Creating new tenants
 
It this section there will be explained possible operations with this endpoint.
 
All operations presented in this document require that user is logged in to platform and has aquired JTW token from
oauth2 server (dex). The token is stored in a config file `.imm`. The user needs to belong to the platform admin group
set during Management API component deployment. 

Login operation is based on Oauth2 process. It can be implemented using [example CLI script](../scripts). 
 
Each tenant is using a dedicated Kubernetes namespace and a bucket in MinIo storage.

To create a tenant it is needed to provide the following parameters:
- tenant name
- CA certificate which is used to sign gRPC authorization client certificates. It will be stored in K8S secret 
‘ca-cert-secret’ in the tenant namespace. Certificate should be decoded by base64
- scope name which represents a group in JWT token
- quota – see Quota configuration for tenants.

After successful operation there are created the following resources:
- new K8S namespace
- a set of K8S secret records storing required credentials and TLS certificates 
- K8S role binding for the defined users group from IdP
- MinIo bucket with the same name like the tenant and the namespace 


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
[K8S documentation](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/).  	
 
Additionally, it is possible to specify how many endpoints can be created within a tenant. 
To do that, use a parameter `maxEndpoints`.
 
Check for the API example on [Management API doc](../management) and review [example CLI](../scripts).


### Listing tenants

Platform Admin can list names of tenants using a list tenants operation.

Check for the API example on [Management API doc](../management) and review [example CLI](../scripts).


### Deleting a tenant

*WARNING*

Deleting tenants is irreversible.

It removes all the K8S records associated with the tenant namespace and drop the tenant MinIo bucket. 

Check for the API example on [Management API doc](../management) and review [example CLI](../scripts).

##
## Creating client certificates 

Before gRPC clients will be able to connect to the Inference Endpoints there should be generated for them
a client TLS certificate which will authenticate and authorize the client to connect to the nginx ingress interface.

The client certificate needs to be signed by the CA certificate which was associated with the tenant during its creation
by the Platform Admin.

Here is the explanation of the anticipated process:
- Tenant organization representative should generate a CA certificate using a command similar to:

```bash
openssl genrsa -des3 -out ca.key 4096 # it stored the private key encrypted
or
openssl genrsa -out ca.key 4096 # it stored the private key in plain text

openssl req -new -x509 -days 3650 -key ca.key -out ca.crt
```

The file `ca/ca.key` should be stored securely by the users. It will be needed to create client certificates.

The file `ca/ca.crt` needs to be passed to the Platform Admin to associate it with the new tenant.

- Anyone can create the request for the client certificates with the following commands:
```bash
openssl genrsa -out client/client.key 4096
openssl req -key client/client.key -new -out client/client.req # It will prompt for cert info including Common Name (Subject Name)
```

This `client.req` should be passed to the tenant user with the access to `ca.key` to generate the client certificate:
```bash
openssl x509 -req -sha256
 -in client.req -CA ca.crt -CAkey ca.key -CAserial ca/file.srl -out client.crt
```
The generated `client.crt` should be returned to the user requesting the certificates.

`client.crt` together with `client.key` can be used to authorize the client against the nginx ingress endpoints via MTLS.

- Note that the Inference Endpoints needs to be configured to allow connections for the clients matching the certificate 
`Subject Name` and signed by the appropriate CA configured in the tenant.

Refer to [gRPC example client](../examples/grpc_client) to see how the credentials should be used by the client.
