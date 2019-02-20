# Installation

## Prerequisites
* [yq](https://github.com/mikefarah/yq) *(Use this specific version of yq)*
* [jq](https://stedolan.github.io/jq/)
* [helm](https://github.com/helm/helm)
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
* [kops](https://github.com/IntelAI/inference-model-manager/tree/master/kops) or other tool for
  creating k8s cluster (if needed)
* unbuffer
  * ubuntu: `sudo apt-get install expect-dev` or `sudo apt-get install expect`
  * for mac it is downloaded during installation
* `export GOOGLE_APPLICATION_CREDENTIALS` if using kops (or use -g switch with installer)  
* domain for IMM

## Run
* Required optons:
  * `-k` - cluster name
  * `-d` - domain name
* Additional options
  * `-z` - GCE cluster zone (if using kops and GCE)
  * `-q` - silent mode (shows only important logs)
  * `-s` - skip cluster creation via kops
  * `-g` - GCE user name (usually email), used to create cluster in GCE
  * `-h/?` - show help
* Usage examples  
  * `./install.sh -k <name> -d <domain>`
  * `./install.sh -k <name> -d <domain> -z <gce_zone> -g john.doe@example.com`
  * `./install.sh -k <name> -d <domain> -s -q`

### Update DNS records for new domain
#### Using AWS Route53
* set up [awscli](https://aws.amazon.com/cli/)
* ```aws configure```
* create
```
cd utils/route53
./apply.sh CREATE $IP_ADDRESS $DOMAIN_NAME
```
* delete
```
cd utils/route53
./apply.sh DELETE $IP_ADDRESS $DOMAIN_NAME
```

## Tests
* Prerequisites:
  * python3.6 or higher
  * installed certificates 
     ```
     sudo cp inference-model-manager/helm-deployment/management-api-subchart/certs/ca-ing-mgt-api.crt /usr/local/share/ca-certificates/ca-ing-mgt-api.crt
     sudo cp inference-model-manager/helm-deployment/dex-subchart/certs/ca-ing-dex.crt /usr/local/share/ca-certificates/ca-ing-dex.crt
     sudo update-ca-certificates
     ```
  * installed dependencies
      ```
      pip install -r inference-model-manager/tests/requirements.txt
      pip install -r inference-model-manager/examples/grpc_client/requirements.txt
      ```
  * exported variables
      ```
      cd inference-model-manager/

      export DOMAIN_NAME=<your_domain>
      export DEX_DOMAIN_NAME="dex.${DOMAIN_NAME}"
      export MGMT_DOMAIN_NAME="mgt.${DOMAIN_NAME}"
      export DEX_NAMESPACE="dex"
      export MGT_NAMESPACE="mgt-api"
      export DEX_URL=https://${DEX_DOMAIN_NAME}:443
      export CERT=`cat ./helm-deployment/management-api-subchart/certs/ca-cert-tf.crt | base64 -w0`
      export REQUESTS_CA_BUNDLE=/etc/ssl/certs/
      ```
* Run smoke tests available
  [here](https://github.com/IntelAI/inference-model-manager/blob/installer-bszelag/scripts/test_imm.sh)
  ```
  cd scripts/
  ./test_imm.sh
  ```
