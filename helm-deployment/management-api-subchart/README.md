## Helm deployment of Management-api

### Preparation to installation

You have to set all values specify in this chapter to properly run this chart
```image: <crd_image_path> - path to image
   tag: <crd_image_tag> - iamge tag
   ingress:
     hosts: <management_api_desired_dns> - address to management api
     tls:
        hosts: <management_api_desired_dns> - address to management api
   resources: {} - it`s optionall, if you want you can specify resources for dex
   platformDomain: - platform dns
```
Also you have to make sure that you already have deploy ```minio-access-info``` secret.
Platform required ssl to internal traffic. We recommend to use for this purpose our script ```internal_ing_man_api_certs.sh``` located in ```certs``` directory.

### Installation

To install this chart after preparation phase use:
```helm install .```
