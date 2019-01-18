## Helm deployment of Custom resource definition

### Preparation to installation

You have to set all values specify in this chapter to properly run this chart
```image: <crd_image_path> # path to image
   tag: <crd_image_tag> # image tag
   platformDomain: <dns_for_tfs> # platform dns
   private_registry: false # If you use private registry and your cluster do not have access to that registry set this value to "true". Below you can see what else you need to do 
```
#### Private docker registry

If you in previous step set docker_secret variable to ``true`` you have to create a secret in the cluster which holds your authorization token. Whole process is described [here](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#create-a-secret-in-the-cluster-that-holds-your-authorization-token).

#### Serving templates

Under ``serving-templates`` directory could be found serving templates, which be used by CRD.
By default, 2 templates are available after creating the CRD ``tf-serving`` and ``ovms``.

You can add your own [templates](../../docs/serving_templates.md). Under ``serving-templates`` create new directory, which be name for serving-template(Name of that directory must be longer than 3 chars and can`t contain '_'). 
In created directory must be 4 yaml files with exactly the same names, as mentioned below:
```
deployment.tmpl
ingress.tmpl
service.tmpl
configMap.tmpl
```

Other hints and requirements can be read [serving-templates readme file](../../docs/serving_templates.md).


### Installation

To install this chart after preparation phase use:
```helm install .```
