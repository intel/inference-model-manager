# Helm deployment of Ingress Nginx Controller

## Preparation to installation

Before installation is required to specify type of k8s cluster.
If you use Google Cloud as your k8s provider you have to specify ```ingType``` value as ``cloud-generic``. 
If you have k8s installed on bare metal you have to specify ```ingType``` value as ``baremetal``.

In case you use another providers please check process of deployment in this [guide](https://github.com/kubernetes/ingress-nginx/blob/master/docs/deploy/index.md)

## Installation

To install this chart after preparation phase use:

```helm install .```