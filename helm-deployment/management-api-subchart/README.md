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
Platform required ssl to internal traffic. We recommend to use for this purpose our script ```generate-management-api-certs.sh``` located in ```certs``` directory.
Before running the script mentioned above, set the environment variable ```MGT_NAMESPACE```

### Installation

To install this chart after preparation phase use:
```helm install .```


## MANUAL STEP REQUIRED TO USE MINIO WITH SELF-SIGNED CERTIFICATES

Assumed that tls-ssl-minio is secret created as described in https://github.com/minio/minio/tree/master/docs/tls/kubernetes

Add following sections to management-api deployment


```
kubectl edit depoyment management-api
```

```yaml
   - mountPath: /minio-CA/
       name: secret-volume

```

```yaml
   - name: secret-volume
        secret:
          defaultMode: 420
          items:
          - key: public.crt
            path: CAs/public.crt
          secretName: tls-ssl-minio
```

```yaml
    - name: AWS_CA_BUNDLE
        value: /minio-CA/CAs/public.crt
```

Edit secret with minio access information:

```
kubectl edit secret minio-access-info
```

Replace current value of minio.endpoint_url with your minio url, started with https, base64 encoded.

### MANUAL STEPS REQUIRED TO REPLACE MINIO WITH AWS S3

Edit secret with minio access information:
```
kubectl edit secret minio-access-info
```

Repalce current values of minio access details with your s3 access details.
```
AWS_ACCESS_KEY_ID=XXXXX
AWS_SECRET_ACCESS_KEY=XXXXX
AWS_REGION=<region>
S3_ENDPOINT=s3.<region>.amazonaws.com
S3_USE_HTTPS=1
S3_VERIFY_SSL=1
```
NOTE: Do not use general aws s3 url: s3.amazonaws.com, location is needed

