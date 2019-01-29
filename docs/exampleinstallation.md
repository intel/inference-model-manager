# Example installation guide for IMM deployment with Ldap, MinIo and self-signed certificates
## Requirements checklist
- Kubernetes cluster 1.8 or above, with RBAC enabled and access to api-server
- Access to Minio compatible storage 
- Access to docker registry 
- Identity provider supported by DEX connectors
- DNS records for Management API, oauth2 server and Inference Endpoints
  Inference Model Manager requires DNS CNAME records pointing to ingress-nginx service. Later in this procedure this domain will be called imm.example.com. This example installation guide needs mgt.imm.example.com for Management API, dex.example.com for Dex, and wildcard *.grpc.example.com for inference endpoints.
- helm installed https://docs.helm.sh/using_helm/

Before installation of IMM, make sure to have following:

- Access to kubernetes cluster with ```kubectl``` 
- Helm command installed ```helm``` and ```tiller``` configured
- Minio compatible storage ```address, access key, secret key```
- fully qualified domain name, eg: ```imm.example.com```
- Access to one of the identity provider supported by DEX: LDAP, GitHub, SAML 2.0, GitLab	
                                                OpenID Connect, LinkedIn, Microsoft
- Docker registry url (REGISTRY_URL)


## Installation steps

### 1.Clone inference-model-manager repo
```
git clone https://github.com/IntelAI/inference-model-manager.git
```
### 2.Configure CRD chart and install it 
```
vim inference-model-manager/helm-deployment/crd-subchart/values.yaml
- replace 
<dns_domain_name> with imm.example.com
cd inference-model-manager/helm-deployment/crd-subchart/
helm install .
```
Check installation
Issue command
``` 
kubectl get pods -n crd
```
Expected output:
```
NAME                                READY     STATUS             RESTARTS   AGE
server-controller-c989895b7-pvh55   1/1       Running   0                   17s
```
### 3. Install ingress-nginx
Go to inference-model-manager/helm-deployment/ing-subchart/, open values.yaml file and fill in your environment type (cloud or bare metal).
Run
```
helm install .
```
If your environment is bare metal and you want to use Kubernetes Node Port, please take a look on docs/nodeport.md file.


### 4. Choose storage provider
For storing AI models you can choose any S3 compatible provider. If you already have Minio/S3 or other component, Management Api installation guide will show you how to integrate it with our pltform. If not, commands below show how to deploy example Minio component.

```
cd inference-model-manager/helm-deployment/minio-subchart/
vi values.yaml #type desired credentials
helm dep up .
helm install .
```

### 5. Install DEX Oauth2Server [dex doc]
In this step you need to configure DEX connection to identity provider, like LDAP.
Sample dex configuration for LDAP: https://github.com/dexidp/dex/blob/master/examples/config-ldap.yaml
Create certificates using inference-model-manager/helm-deployment/dex-subchart/generate-dex-certs.sh and generate-ing-dex-certs.sh scripts. Remember to export DEX_NAMESPACE, DEX_DOMAIN_NAME and ISSUER environment variables, before running those scripts.
Format of above variables should fit following patterns:
```
export ISSUER=https://dex.imm.example.com:443/dex # change 443 port if using kubernetes node port instead of load balancer
export DEX_NAMESPACE=dex
export DEX_DOMAIN_NAME=dex.imm.example.com
```
Generate certificates:
```
cd inference-model-manager/helm-deployment/dex-subchart/certs
./generate-dex-certs.sh 
./generate-ing-dex-certs.sh
```

Following commands deploy Dex and Ldap with our example configuration.
```
cd inference-model-manager/tests/deployment/
helm install --name imm-ldap -f ldap/values.yaml stable/openldap
```
After successful deployment (pod is up and running) of ldap run:

```
cd inference-model-manager/tests/deployment/
sed -i "s@toreplacedbyissuer@${ISSUER}@g" dex_config.yaml
export OPENLDAP_SVC=`kubectl get svc|grep "openldap   "| awk '{ print $1 }'`
export OPENLDAP_SVC_ADDRESS="$OPENLDAP_SVC.default:389"
sed -i "s@toreplacebyldapaddress@${OPENLDAP_SVC_ADDRESS}@g" dex_config.yaml
helm install -f dex_config.yaml --set issuer=${ISSUER} --set ingress.hosts=${DEX_DOMAIN_NAME} --set ingress.tls.hosts=${DEX_DOMAIN_NAME} ../../helm-deployment/dex-subchart/

```

After this step dex pod should be running in dex namespace:

Execute:
```
kubectl get pods -n dex
```
Expected output:
```

NAME                   READY     STATUS    RESTARTS   AGE
dex-6f8d94bd5f-9vlvm   1/1       Running   1          1m
```
### 6. Install Management API [management api doc]
In this step it's important to setup following variables in values.yaml file.

NOTE: minio_endpoint_url should contain http or https and port number if different than 443.

NOTE: minio_endpoint should contain port number if different than 443

- <management_api_desired_dns> should be a subdomain of your FQDN, like mgt.imm.example.com
- <dns_for_inference_endpoints> could be your domain name, like imm.example.com
- <minio_access_key>  Minio compatible storage access key
- <minio_secret_key> Minio compatible storage secret key
- <minio_endpoint> set to s3.\<region\>.amazonaws.com in case of AWS S3, set to minioplatfrom.default:9000 in case of minio from our default deployment
- <minio_endpoint_url> set to s3.\<region\>.amazonaws.com in case of AWS S3, set to http://minioplatfrom.default:9000 in case of minio from our default deployment
- adjust \<groupName\>, \<adminScope\> and \<platformAdmin\> to match administrative group from Identity Provider
  ,like "admin"
  Users belonging to administrative group will have permissions for tenant administration.

Run our scripts to generete self-signed certificates inference-model-manager/helm-deployment/management-api-subchart/certs/generate-ing-management-api-certs.sh, generate-management-api-certs.sh and scriptcert.sh.

Remember to export following environment variables before running those scripts: MGMT_DOMAIN_NAME, MGT_NAMESPACE, DOMAIN_NAME. Values of those variables should fit following format:
```
export MGMT_DOMAIN_NAME=mgt.imm.example.com
export MGT_NAMESPACE=mgt-api
export DOMAIN_NAME=imm.example.com
```
```
cd inference-model-manager/helm-deployment/management-api-subchart/certs
./generate-ing-management-api-certs.sh
./generate-management-api-certs.sh 
./scriptcert.sh
cp ../../dex-subchart/certs/ca-dex.crt .
```

```
cd inference-model-manager/helm-deployment/management-api-subchart
vim values.yaml
# configure management api here
helm install .
```
Check the installation
```
kubectl get pods -n mgt-api
NAME                              READY     STATUS    RESTARTS   AGE
management-api-5c45d856c7-4kzv4   1/1       Running   0          8s
```
### 7. Enable openId authentication in kubernetes api server
You need to restart kubeapi-server after changes.
Use this link for details https://github.com/IntelAI/inference-model-manager/blob/update-docs/docs/deployment.md#kubernetes-configuration-for-oid-authentication
  
### 8. Verify installation
Obtain token from dex
```
cd scripts
python webbrowser_authenticate.py
# enter your admin credentials here (from LDAP or other configured Identity Provider)
# token should be stored in ~/.imm file
```
Create a test tenant with cli script
(please note that tenant_scope must match Identity Provider group, like "team-name")
```
./api_call.sh create t tenant_name tenant_scope 
```
Ensure tenant is created, by listing kubernetes namespaces
```
kubectl get ns
```
Expected output should contain line:
```
tenant_name   Active    1d
```
At this point, platform is up and running!


