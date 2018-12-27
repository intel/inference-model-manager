# Deployment guide 

## CRD controller

CRD controller record should be created in a dedicated namespace which is not accessible by the unauthorized users to 
protect access to stored secret records.
A prerequisite for the CRD controller functionality is the presence of [nginx ingress controller](https://github.com/kubernetes/ingress-nginx).
 
It should be deployed using created helm chart [ing-subchart](../helm-deployment/ing-subchart) or existing nginx controller 
should be adjusted to include the required changes in nginx template. 

There should be also accessible Minio service. The person deploying the platform need to know Minio endpoint URL,
access key id and access secret.

CRD controller will be creating ingress records for defined inference endpoints relying on the TLS endpoint certificates 
stored in the Kubernetes secret “tls-secret”.

The certificate needs to be valid for a common name with a wildcard matching all gRPC endpoints DNS names 
like *.<grpc_dns_domain>. 

Alternatively, there could be used just a single DNS domain name and certificate for all the platform endpoints but that
would require adjustments in the grpc client code to include in the requests headers also the option 

`grpc.ssl_target_name_override`. This way the clients would connect to a single DNS domain name but the ingress
controller will route the requests to the correct backend services based on hostname specified in ssl_target_name_override
parameter.

The certificate can be self-signed or created by a trusted CA. 
The important note is that the clients connecting to the inference endpoints need to have a trust established with this 
certificate (they need the CA certificate to be present on the client host).

The secret  “tls-secret” will need to be present in every K8S namespace with CRD and ingress records. 
This secret is populated automatically to new namespaces during the new tenant creating operation by Management API.
 
Deployment steps of the CRD controller is arranged by a helm chart. Execute the steps covered on 
[chart doc](../helm-deployment/crd-subchart)  

While the CRD controller is successfully deployed and configured you should be able to test inference endpoint
provisioning by using the [example crd](../examples/crd/example-inference-endpoint.yaml)

## DEX oauth2 server

[Dex](https://github.com/dexidp/dex) is an oauth2 server which can mediate with external Identity Providers 
like LDAP, Github, Facebook and many others.
The installation and configuration of DEX component might depend on the used connector and the type of IdP you would like to use.
We automated and tested the installation process for LDAP integration. For other IdPs refer to the documentation of 
[dex connectors](https://github.com/dexidp/dex/tree/master/connector)  

DEX with LDAP integration can be installed using helm chart from [chart](../helm-deployment/dex-subchart). 
DEX installation should be done in a dedicated namespace this is has access protected from unauthorized users. 
Before you start the installation you need to update the chart values.yaml with the following information:

Deploy DEX server using steps described in [helm chart](../helm-deployment/dex-subchart)

	
## Kubernetes configuration for oid authentication

Because all the platform related changes in Kubernetes are done using user token, the API interface of Kubernetes needs
to be configured to use OID authentication. The details of the process of enabling OID token authentication might
depend on the installation process and specific configuration in the cluster. 
The general steps are documented on 
[K8S authentication](https://kubernetes.io/docs/reference/access-authn-authz/authentication/#openid-connect-tokens).

Specifically kube-apiserver component in kubernetes needs to have included additional parameters during the start up:


| Kube-apiserver parameter | Description | Example |
| ------------- |:-------------:| ------|
| --oidc-issuer-url | URL to DEX endpoint exposed in ingress | https://dex.domain.com/dex |
| --oidc-client-id | client id configured in DEX | infer-platform |
| --oidc-username-claim | the field from the token which identifies the user | email |
| --oidc-username-prefix | optional prefix to user name on K8S side | infer: |
| --oidc-groups-claim | the claim name from JWT token scope | group |
| --oidc-groups-prefix | optional prefix to group name on K8S side | infer: |
| --oidc-ca-file | CA certificate used in DEX endpoint | /etc/kubernetes/ssl/dex_ca.crt |

`oidc-ca-file` parameter is needed in case DEX URL is exposed via ingress with self-signed certificate 
(needed to establish a trust with DEX service to validate the tokens).

## Management API server

Deployment of management API can be completed when the prerequisites are met and remaining platform components are 
deployed (CRD, DEX, K8S API with OID, Minio)

Management API can be deployed using a helm chart. Follow the steps described on
[chart](../helm-deployment/management-api-subchart)

### Troubleshooting
Please refer to:
[Troubleshooting](docs/troubleshooting.md)

