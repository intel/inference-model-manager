## Helm deployment of Dex

### Preparation to installation

You have to set all values specify in this chapter to properly run this chart
```issuer: "none" - issuer must be the same like in dex config
   config:
     <There you can put your dex config>
   resources: {} - it`s optionall, if you want you can specify resources for dex
```

Inference Model Manager requires TSL for internal traffic. We recommend to use for this purpose our script ```generate-dex-certs.sh``` located in ```certs``` directory.
We also provide script to generate self-signed certificates for dex for external traffic. It can be found in following path: ```inference-model-manager/helm-deployment/dex-subchart/certs/generate-ing-dex-certs.sh```
Before running scripts mentioned above, set the environment variable ```DEX_NAMESPACE, DEX_DOMAIN_NAME, ISSUER```
Format of above variables should fit following patterns:
```
export ISSUER=https://dex.<your domain>:443/dex # change 443 port if using kubernetes node port instead of load balancer
export DEX_NAMESPACE=dex # change value of this variable only if you understand consequences
export DEX_DOMAIN_NAME=dex.<your domain>
```


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

