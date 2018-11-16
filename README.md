## Inferno Platform
[![CircleCI](https://circleci.com/gh/NervanaSystems/inferno-platform.svg?style=svg&circle-token=677ac34c125509e550220a080f4f8f68dfb8729c)](https://circleci.com/gh/NervanaSystems/inferno-platform)

**Inferno Platform** is built on top of Kubernetes and provides solution for deploying, hosting and 
managing inference processing endpoints exposed over gRPC protocol.  
 
Two types of interfaces are presented:
* Management API with token based authentication and authorization,
* gRPC Inference Endpoints with MTLS client authentication and Tensorflow Serving API.

##
#### Management API
Management API has two primary functions:
* manage the AI models stored in Minio buckets using access control based on OpenID tokens,
* provide REST API for managing tenants and inference endpoints instead of using Kubernetes API 
or kubectl commands directly.  

#### Inference Endpoints
Each model is represented as Inference Endpoint and hosted as Tensorflow Serving instance. They are 
accessible externally via well-known URL.

For more information about managing tenants, endpoints and models see 
[Management API overview](./management/README.md)  
For example usage of platform see [example client for Resnet model](./examples/grpc_client/README.md)

##
### Third-party components
* Minio/S3 for model storage
* Identity provider which could be LDAP, GitHub or other provider supported by DEX

##
#### Cluster creation

See [kops deployment](./kops/README.md)

##
#### Platform deployment

See [deployment instruction](./helm-deployment/README.md)
