
# Server controller

It is implementation of custom resource definition controller aimed to automate Tensorflow Serving instances management.

## Local development

### Prerequisites
It is golang project so you need to [prepare workspace](https://golang.org/doc/code.html) in order to easily develop it.
In order to re-generate deep copy operations for CRD structures you will need deepcopy package.
        go get github.com/kubernetes/gengo/examples/deepcopy-gen

All project dependencies are managed by dep tool.
```
curl https://raw.githubusercontent.com/golang/dep/master/install.sh | sh
cd server-controller/
dep ensure -v
```

Note: dep tool will need to download dependencies from private repos.
In order to support private repos introduce ~/.netrc file with your token.
Instructions on how to do it correctly can be found [here](https://github.com/golang/dep/blob/master/docs/FAQ.md#how-do-i-get-dep-to-consume-private-git-repos-using-a-github-token).

### Building
In order to build server-controller locally please use following command
```go build -v -i .```

```
## Production build
For production usage Dockerfile.prod shall be built and deployed.
To do so please use following make command:
```
# assuming you are in ./inferno-platform/server-controller
# and ~/.netrc file is prepared and located here
make circleci
```

## Local execution
Server controller requires $PLATFORM_DOMAIN environment variable to be set. It shall contain domain name for the system, controller will operate in.
As a result endpoints created by it will be distunguishable from each other thanks to subdomains in one provided domain (e.g. endpointName-namespace.PLATFORM_DOMAIN).
```
# Assumes you have a working kubeconfig. Not required if operating in-cluster.
export PLATFORM_DOMAIN=some-domain.com
./server-controller -kubeconfig=$HOME/.kube/config
```

## Use Cases

### Creation of new Tensorflow Serving instance.
In order to create new Tensorflow Serving instance you need to provide description of it in Yaml file form.
To see reference go to CRD definition in inferno-platform/CRD. There is one resource file with example called example-server.yaml.
In order to add it to existing kubernetes just type:
```kubectl create -f example-server.yaml```

Server-controller will spin new deployment, service and ingress record for you.

### Resources removal
In order to remove all resources that sums up to your Tensorflow Serving instance just remove CRD resource you introduced:
```kubectl delete servers.aipg.intel.com my-super-server```


