## Helm deployment of Dex

### Preparation to installation

You have to set all values specify in this chapter to properly run this chart
```  accessKey: <minio_access_key>
     secretKey: <minio_secret_key>
```

### Installation

To install this chart after preparation phase use:
```helm install .```

### MANUAL STEPS REQUIRED TO SECURE MINIO WITH TLS (SELF-SIGNED CERTIFICATES)

Assumed that self-signed certificate and key is placed in current directory. Cert and key file name is important.
Create kubernetes secret.

```
kubectl create secret generic tls-ssl-minio --from-file=./private.key --from-file=./public.crt

kubectl edit deployment minioplatform
```

Follow instructions from https://github.com/minio/minio/tree/master/docs/tls/kubernetes#3-update-deployment-yaml-file
