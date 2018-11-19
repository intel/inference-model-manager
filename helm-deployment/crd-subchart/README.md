## Helm deployment of Custom resource definition

### Preparation to installation

You have to set all values specify in this chapter to properly run this chart
```image: <crd_image_path> - path to image
   tag: <crd_image_tag> - iamge tag
   docker_secret: false - if your cluster doesnt have access you have to specify credentials to pull image
   platformDomain: <dns_for_tfs> - platform dns
   minio:
     secretCreate: true - if you already create minio secret, set this to false
     accessKey: <minio_access_key>
     secretKey: <minio_secret_key>
     endpoint: <minio_endpoint>
     endpointUrl: <minio_endpoint_url>
     minioRegion: "us-east-1" - if you use other region, change this
     minioSignatureVersion: "s3v4" - if you use toher signature, change this
```

### Installation

To install this chart after preparation phase use:
```helm install .```
