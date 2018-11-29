# Helm deployment of Management-api

## Preperations

Generate K8S cluster internal TLS certificates to be used in Management API component
```
cd helm-deployment/management-api-subchart/certs/
export MGT_NAMESPACE=<namespace for mgt api>
./generate-management-api-certs.sh
```

Generate external TLS certificates to ingress or arrange trusted certificates from your CA and place them with the same
names in certs folder. 
```
./generate-ing-management-api-certs.sh
```
For security reasons it is strongly recommended to secure external ingress endpoints using TLS certificates from a 
trusted Certificate Authority.

## Installation

Adjust the helm chart `values.yaml` as needed. Specifically set:

```
minio.endpoint - minio clusterIP and port for example "minio.namespace:9000" 
MINIO_URL - for example "http://minio.namespace:9000
image - docker image name with Management API component
tag - docker image tag with Management API component
platformDomain - DNS domain to be used for new Inference Endpoints
ingress.hosts,ingress.tls.hosts - DNS name for the Management API external interface
minio.accessKey - MinIo access key
minio.secretKey - MinIo secret
platformAdmin - the group with Platform admin permissions - should match JWT token groups scope
```

The group set in `platformAdmin` parameter is being granted kubernetes cluster role binding to enable managing 
all inferenece tenanats and kubernetes namespaces.
 
In case `dexUrl` is pointing to dex internal service name which is protected using a TLS certificate with a self-signed CA,
you need to copy the dex CA certificate to `certs` folder with a name `ca-dex.crt`. This way Management API will be
able to connect securely with the dex endpoints.
When `dexUrl` is using external ingress URL with a trusted certificate this step is not required.


Execute helm installation via:
```
helm install .
```

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


## MANUAL STEPS REQUIRED TO REPLACE MINIO WITH AWS S3

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

