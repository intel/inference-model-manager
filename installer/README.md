# Installation

## Prerequisites
* [yq](https://github.com/mikefarah/yq)

## Run
* ./install.sh -k <name> -d <domain>

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




