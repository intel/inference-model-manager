# Installation

## Prerequisites
* [yq](https://github.com/mikefarah/yq)
* [kops](https://github.com/IntelAI/inference-model-manager/tree/master/kops) or other tool for
  creating k8s cluster
* unbuffer
  * ubuntu: `sudo apt-get install expect-dev` or `sudo apt-get install expect`
  * for mac it is downloaded during installation
* `export GOOGLE_APPLICATION_CREDENTIALS` if using kops  

## Run
* `./install.sh -k <name> -d <domain>`

### Update DNS records for new domain
#### Using AWS
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




