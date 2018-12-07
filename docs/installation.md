
## Requirements checklist
- Kubernetes cluster 1.8 or above, with RBAC enabled and access to api-server
- Access to Minio compatible storage 
- Access to docker registry 
- Identity provider supported by DEX connectors
- DNS records for Management API, oauth2 server and Inference Endpoints
- helm installed https://docs.helm.sh/using_helm/

Before installation of IMM, make sure to have following:

- Access to kubernetes cluster with ```kubectl``` 
- Helm command installed ```helm```
- Minio compatible storage ```address, access key, secret key```
- fully qualified domain name, eg: ```imm.example.com```
- Access to one of the identity provider supported by DEX: LDAP, GitHub, SAML 2.0, GitLab	
                                                OpenID Connect, LinkedIn, Microsoft
- Docker registry url (REGISTRY_URL)


## Installation steps

### 1.Install tiller on kubernetes cluster

```
kubectl -n kube-system create serviceaccount tiller

kubectl create clusterrolebinding tiller \
  --clusterrole cluster-admin \
  --serviceaccount=kube-system:tiller

helm init --service-account tiller
```

### 2.Clone inference-model-manager repo
```
git clone git@github.com:IntelAI/inference-model-manager.git
```
### 3.Build CRD controller image and push to docker registry
```
cd inference-model-manager/server_controller
make docker_build
```
obtain IMAGE_ID using 
```
docker images
```
tag and push the image
```
docker tag $IMAGE_ID $REGISTRY_URL/server-controller-prod:latest
docker push $REGISTRY_URL/server-controller-prod:latest
```
### 4.Configure CRD chart and install it 
```
vim inference-model-manager/helm-deployment/crd-subchart/values.yaml
- replace 
<crd_image_path> with $REGISTRY_URL/server-controller-prod
<crd_image_tag> with latest 
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

### 5. Install DEX Oauth2Server [dex doc]
In this step you need to configure DEX connection to identity provider, like LDAP.
Sample dex configuration for LDAP: https://github.com/dexidp/dex/blob/master/examples/config-ldap.yaml
```
cd inference-model-manager/helm-deployment/dex-subchart
vim values.yaml
# enter dex configuration here, use link above if necessary
helm install .
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
### 6. Build Management API and push image to registry
```
cd inference-model-manager/management
make docker_build
```
get the IMAGE_ID using 
```
docker images
```
Tag and push the image to registry
```
docker tag $IMAGE_ID $REGISTRY_URL/management-api:latest
docker push $REGISTRY_URL/management-api:latest
```

### 7. Install Management API [management api doc]
In this step it's important to setup following variables in values.yaml file:

- <image_path> $REGISTRY_URL/management-api
- <image tag> use "latest"
- <management_api_desired_dns> should be a subdomain of your FQDN, like mgt.imm.example.com
- <dns_for_inference_endpoints> could be your domain name, like imm.example.com
- <minio_access_key>  Minio compatible storage access key
- <minio_secret_key> Minio compatible storage secret key
- <minio_endpoint> not used, set to s3.<region>.amazonaws.com
- <minio_endpoint_url> s3.<region>.amazonaws.com
- adjust <groupName>, <adminScope> and <platformAdmin> to match administrative group from Identity Provider
  ,like "admin"
  Users belonging to administrative group will have permissions for tenant administration.
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
### 8. Enable openId authentication in kubernetes api 
You need to restart   
Use this link ahttps://github.com/IntelAI/inference-model-manager/blob/update-docs/docs/deployment.md#kubernetes-configuration-for-oid-authentication
  
### 9. Verify installation
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


