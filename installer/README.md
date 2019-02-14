# Installation

## Prerequisites
* [yq](https://github.com/mikefarah/yq)
* [jq](https://stedolan.github.io/jq/)
* [helm](https://github.com/helm/helm)
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
* [kops](https://github.com/IntelAI/inference-model-manager/tree/master/kops) or other tool for
  creating k8s cluster (if needed)
* unbuffer
  * ubuntu: `sudo apt-get install expect-dev` or `sudo apt-get install expect`
  * for mac it is downloaded during installation
* `export GOOGLE_APPLICATION_CREDENTIALS` if using kops  

## Run
* `./install.sh -k <name> -d <domain>`

### Update DNS records for new domain
#### Using AWS
* set up [awscli](https://aws.amazon.com/cli/)
* create
```
cd utils/dns_utils
edit file route_record.json
./create_domain.sh
```
* delete
```
cd utils/dns_utils
edit file route_record.json
./create_domain.sh
```

## Tests
* Prerequisites:
  * python3.6 or higher
  * run smoke tests available
  [here](https://github.com/IntelAI/inference-model-manager/blob/installer-bszelag/scripts/test_imm.sh)
      ```
      cd inference-model-manager/

      export CLUSTER_NAME_SHORT=<your_cluster_name>
      export REQUESTS_CA_BUNDLE=/etc/ssl/certs/
      export DEX_DOMAIN_NAME="dex.${CLUSTER_NAME_SHORT}.nlpnp.adsdcsp.com"
      export MGMT_DOMAIN_NAME="mgmt.${CLUSTER_NAME_SHORT}.nlpnp.adsdcsp.com"
      export DOMAIN_NAME="${CLUSTER_NAME_SHORT}.nlpnp.adsdcsp.com"
      export DEX_NAMESPACE="dex"
      export MGT_NAMESPACE="mgt-api"
      export DEX_URL=https://${DEX_DOMAIN_NAME}:443
      export CERT=`cat ./helm-deployment/management-api-subchart/certs/ca-cert-tf.crt | base64 -w0`

      cd scripts/
      ./test_imm.sh
      ```



