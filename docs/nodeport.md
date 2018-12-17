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
