
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
Details can be found [here](https://github.com/golang/dep/blob/master/docs/FAQ.md#how-do-i-get-dep-to-consume-private-git-repos-using-a-github-token).

### Building
In order to build server-controller locally please use following command
```go build -v .```

You can also use Dockerfiles in order to development images.
There is Dockerfile for production images available, also. It is cover in next section.

Development Dockerfile usage (requires filled .netrc file in server-controller directory!):
```
cd server-controller
docker build -f Dockerfile.dep -t server-controller-dep .
docker build -f Dockerfile.devel -t server-controller .
```
## Production build
Production image does not hold all development related things like curl, netcat etc.
To succesfully prepare such image build server-controller locally first. "server-controller" binary shall appear in directory. Then execute:
```
# assuming you are in ./inferno-platform/server-controller
# and server-controller binary is built and located here
docker build -f Dockerfile.prod -t server-controller .
```

## Local execution
```
# assumes you have a working kubeconfig, not required if operating in-cluster
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
```kubectl delete servers.intel.com my-super-server```


