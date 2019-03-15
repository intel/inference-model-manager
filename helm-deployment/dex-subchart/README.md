## Helm deployment of Dex

### Preparation to installation

You have to set all values specify in this chapter to properly run this chart
```issuer: "none" - issuer must be the same like in dex config
   config:
     <There you can put your dex config>
   resources: {} - it`s optionall, if you want you can specify resources for dex
```

Inference Model Manager requires TLS certficates to secure internal K8S endpoints. We recommend to use for this purpose our script ```generate-dex-certs.sh``` located in ```certs``` directory.
We also provide script to generate self-signed certificates for dex for external traffic. It can be found in following path: ```inference-model-manager/helm-deployment/dex-subchart/certs/generate-ing-dex-certs.sh```
Before running scripts mentioned above, set the environment variable ```DEX_NAMESPACE, DEX_DOMAIN_NAME, ISSUER```
Format of above variables should fit following patterns:
```
export ISSUER=https://dex.<your domain>:443/dex # change 443 port if using kubernetes node port instead of load balancer
export DEX_NAMESPACE=dex
export DEX_DOMAIN_NAME=dex.<your domain>
```
If you are connecting to the Identity provider via secure https connection you might need to configure TLS trust with its endpoint.
It can be done using helm chart parameters:
- `rootCAsecret` - name of the secret to store CA certificate of IdP TLS endpoint.
- `rootCAfile` - if set, it populates the secret named by `rootCAsecret` from the file in PEM format
The CA certificate will be mounted in the dex container in '/etc/dex/ca' folder. You might need to adjust the dex connector configuration to use appropriate path to the certificate.


### Installation

To install this chart after preparation phase use:
```helm install .```

You can also a predefined dex config adjusted for the ldap server. Make sure you adjusted the 
[dex_config.yaml](../../tests/deployment/dex_config.yaml) specific to your LDAP infrastructure unless you use the included
[LDAP example chart](../../tests/deployment/ldap)

```bash
cd tests/deplomnets
source ./deployment_dex.sh
```

## Kubernetes Node Port

Changes required by switching from Load Balancer to Node Port

Replace default 443 port in $ISSUER variable (tests/deployment/dex_config.yaml and tests/deployment/deployment_dex.sh) before running dex deployment with node port.

```
kubectl get svc -n ingress-nginx
NAME                   TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                      AGE
default-http-backend   ClusterIP                   <none>        80/TCP
ingress-nginx          NodePort                    <none>        80:31641/TCP,443:30258/TCP
```
Node port used for https connection can be found next to ingress-nginx kubernetes service.

Add port number to KubeApi server connection to Dex details to oidc issuer url option.

Replace 443 port with node port when using any script that requires connection to Management Api or Dex, ex. scripts/api_call.sh.

Fill in value of DEX_EXTERNAL_URL variable in values.yaml file to end dex url, followed by node port number.
Example:
```
dex.domain.com:30258
```
Note: Remember to deploy ingress-nginx pod to the same host where dns is set to.

