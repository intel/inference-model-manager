## Test deployment

In this directory are scripts, which allows user to easily deploy platform to run tests.

### Preparation to installation

Before installation you have to export all needed environmental variables.

```
export MINIO_ENDPOINT
export MINIO_ACCESS_KEY
export MINIO_SECRET_KEY
export CRD_IMAGE - path to crd image
export CRD_TAG - crd image tag
export DOMAIN_NAME - platform dns
export DEX_INTERNAL_CERTS - it is can be true/false - specify if certs have to be generated used scripts in this repository
export DEX_CERTS - it is can be true/false - specify if certs have to be generated used scripts in this repository
export DEX_DOMAIN_NAME - DNS for dex
export ISSUER - dex issuer
export ING_CERTS - it is can be true/false - specify if certs have to be generated used scripts in this repository
export WRONG_CERTS - it is can be true/false - specify if certs have to be generated used scripts in this repository
export MGMT_INTERNAL_CERTS - it is can be true/false - specify if certs have to be generated used scripts in this repository
export MGMT_CERTS - it is can be true/false - specify if certs have to be generated used scripts in this repository
export MGMT_DOMAIN_NAME - DNS for management-api
export MGMT_IMAGE - path to management-api image
export MGMT_TAG - management-api image tag
```
WARNING!
Remember to fill up ```dex_config.yaml```

### Installation
After set all required environmental variables use this command:
```bash
./deployment_platform.sh
```

