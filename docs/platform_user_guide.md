# User Guide

## Login operation

All operations presented here require that the user is logged in to platform and has acquired JTW token from
oauth2 server (dex). The token is stored in a config file `.imm`. The user needs to belong to the group in the Identity Provider
which was associated with the tenant but the Platform Admin. 

Login operation is based on Oauth2 process. It can be implemented using [example CLI script](../scripts) 

## Uploading AI model

Management API is exposing a set of endpoints which enable uploading AI models to MinIo storage using multipart transfer.
It makes the upload operation reliable and fast even for big model files.

Management API is managing the model versions the same way like TensorFlow Serving does.
Each model name can have a list of versions are needs to be represented by a positive integer number.
In the MinIo it forms a structure of folders like in the example below:
```
bucket_name
    model_name1
        1
            saved_model.pb
        2
            saved_model.pb
     model_name2
        1
            saved_model.pb
```
Inference model servers are automatically pulling the models from the appropriate MinIo path by just referencing the 
tenant name (bucket), model name and model version.

Below are described [example CLI options](../scripts/model_upload_cli.py) for uploading the models.
 

```
python model_upload_cli.py --help
usage: model_upload_cli.py [-h] [--part PART]
                           file_path model_name model_version tenant

Inferno Model Uploader

positional arguments:
  file_path      Path to file with model to upload
  model_name     Name of uploaded model
  model_version  Version of uploaded model
  tenant         Tenant which is uploading model

optional arguments:
  -h, --help     show this help message and exit
  --part PART    Size of data chunk in MB sent in a single upload request
                 (acceptable values: 5-5000, default: 30)
```

## Listing the models

Refer to the Management [API documentation](../management)

## Deleting the models

Refer to the Management [API documentation](../management)

## Creating client certificates 

Before gRPC clients will be able to connect to the Inference Endpoints there should be generated for them
a client TLS certificate which will authenticate and authorize the client to connect to the nginx ingress interface.

The client certificate needs to be signed by the CA certificate which was associated with the tenant during its creation
by the Platform Admin.

Here is the explanation fo the anticipated process:
- Tenant organization representative should generate a CA certificate using a command similar to:

```bash
openssl genrsa -des3 -out ca.key 4096 # it stored the private key encrypted
or
openssl genrsa -out ca.key 4096 # it stored the private key in plain text

openssl req -new -x509 -days 3650 -key ca.key -out ca.crt
```

The file `ca/ca.key` shoudl be stored securely by the users. It will be needed to create client certificates.

The file `ca/ca.crt` needs to be passed to the Platform Admin to associate it with the new tenant.

Anyone can create the request for the client certificates with the following commands:
```bash
openssl genrsa -out client/client.key 4096
openssl req -key client/client.key -new -out client/client.req # It will prompt for cert info including Common Name (Subject Name)
```

This `client.req` should be passed to the tenant user with the access to `ca.key` to generate the client certificate:
```bash
openssl x509 -req -sha256
 -in client.req -CA ca.crt -CAkey ca.key -CAserial ca/file.srl -out client.crt

```
The generated `client.crt` should be returned to the user requesting the certificates.

`client.crt` together with `client.key` can be used to authorize the client against the nginx ingress endpoints via MTLS.

Note that the Inference Endpoints needs to be configured to allow connections for the clients matching the certificate 
`Subject Name` and signed by the appropriate CA configured in the tenant.

Refer to [gRPC example client](../examples/grpc_client) to see how the credentials should be used by the client.

## Creating inference endpoints

Endpoints can be created by using a REST endpoint exposed by Management API with an address:
 `https://<management-api-address>/tenants/<tenant-name>/endpoints`
 
To create an endpoint we need to provide following parameters:
- endpointName - it identifies the endpoint and will compose the URL for the inference clients 
<endpointName><tenant><domain name>
- subjectName - Common Name in the client certificate authorized to access the gRPC Inference Endpoint,
- modelName – model to serve
- modelVersion – version of a model to serve
We can also specify additional parameters:
- replicas – number of replicas to be provisioned
- resources – see Resources for endpoint

Refer to the Management [API documentation](../management) and [example CLI](../scripts) to see 
how the endpoint should be used.


## Resources for endpoints

Similarly to the tenant level quotas it is possible to set endpoint level resource constraints. It can define the 
limits for resource consumption and allocation on a single replica level in the Inference Endpoint.
  
Example of resources could be:
`\”resources\” {\”requests.cpu\”: \”2\”, \”limits.cpu\”: \”4\”}`


## Listing inference endpoints

List endpoint is returning the list of the endpoint names and their status.

Refer to the Management [API documentation](../management) and [example CLI](../scripts) to see 
how the endpoint should be used.


## Deleting inference endpoints

Delete endpoint is removing requests Inference Endpoint records. It is not removing the served model.

Refer to the Management [API documentation](../management) and [example CLI](../scripts) to see 
how the endpoint should be used.

## Viewing inference endpoints

View endpoint is returning the information about the request inference Endpoint:
- status
- model path
- client cert Subject Name 
- resources
- replicas

Refer to the Management [API documentation](../management) and [example CLI](../scripts) to see 
how the endpoint should be used.

## Updating the inference endpoints
 
Update endpoint can change the model served be the endpoint. It accepts the following parametes:
- modelName – name of the model from bucket,
- modelVersion – version of the model from bucket

A change will trigger a rolling update in the Inferece Endpoint replicas.

Refer to the Management [API documentation](../management) and [example CLI](../scripts) to see 
how the endpoint should be used.

## Scaling inference endpoints

Scaling is implementing by changing the number of replicas number of this endpoint. 
Replicas number passed as a parameter for API call, will make a change in a deployment of endpoint’s CRD.
 
Endpoints can be scaled by using a REST endpoint exposed by Management API with an address:
 
```https://<management-api-address>/tenants/<tenant-name>/endpoints/<endpoint-name>/replicas```
 
New replicas will be provisioned uness there are insufficient available resources in the tenant quota, 
or in the cluster. 

It is possible to scale down an endpoint to 0, which means that the endpoint is not in a running state. 
That is a way of “turning off” an endpoint. 
For “turning on” just call a scale operation and change replicas number for a desired number.
 
 
