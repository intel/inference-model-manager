# Server controller

CRD controller installation is extending the Kubernetes API definition to additional CRD record 
type called ‘inference-endpoint’. 
Its definition is included in [crd.yaml](../helm-deployment/crd-subchart/templates/crd.yaml)
The controller is monitoring the status of ‘inference-endpoint’ CRD records and applies required 
changes 
in linked Kubernetes deployments, services and ingress resources. 

This way managing all aspects of serving inference endpoints can be delegated to a single Kubernetes record. 
It makes the management much simpler and allows delegating for the users permissions to manage the inference endpoint 
without exposing other operations and resources in Kubernetes like pods, secrets and config maps.

## Docker image building

```
make docker_build
```
While the docker image is built it should be pushed to a docker registry accessible by the K8S cluster.


## Deployment in Kubernetes cluster

Refer to the [helm chart](../helm-deployment/crd-subchart) documentation. 


## Development guide

### Prerequisites
It is golang project so you need to [prepare workspace](https://golang.org/doc/code.html) 
in order to easily develop it.
In order to re-generate deep copy operations for CRD structures you will need deepcopy package.
```
go get github.com/kubernetes/gengo/examples/deepcopy-gen
```

All project dependencies are managed by dep tool.
```
curl https://raw.githubusercontent.com/golang/dep/master/install.sh | sh
cd server-controller/
dep ensure -v
```

### Inference Endpoint configuration files

Currently all the inference endpoints in the platform are being provisioned using the templates from [resources](resources).
They are fixed at the docker image building time.

In plans is adding more flexibility to define multiple templates at run-time in the form of K8S config maps.


### Local building
In order to build server-controller locally please use following command
```
go build -v -i .
```

### Continuous integration build
For production usage Dockerfile.prod shall be built and deployed.
To do so please use following make command:
```
make circleci
```

### Local execution
Server controller requires $PLATFORM_DOMAIN environment variable to be set. It shall contain domain 
name for the system, controller will operate in.
Endpoints created by the controller will include the domain name (e.g. endpointName-namespace.PLATFORM_DOMAIN)

```
# Assumes you have a working kubeconfig. Not required if operating in-cluster.
export PLATFORM_DOMAIN=some-domain.com
./server-controller -kubeconfig=$HOME/.kube/config
```

### Testing

#### Creation of new inference endpoint.
In order to create new Inference Endpoint you need to provide description of it in a yaml 
file.  There is one resource file
with example called example-inference-endpoint.yaml.
In order to add it to existing kubernetes just type:
```kubectl create -f example-inference-endpoint.yaml```

Server-controller will spin new deployment, service and ingress record for you.

### Resources removal
In order to remove all resources that sums up to your Inference Endpoint just remove CRD 
resource you introduced:
```kubectl delete inference-endpoint example-endpoint```


