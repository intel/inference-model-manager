/*
Copyright 2017 The Kubernetes Authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

// Note: the server only works with the code within the same release/branch.
package main

import (
	"context"
	"errors"
	"flag"
	apiv1 "k8s.io/api/core/v1"
	extv1beta1 "k8s.io/apiextensions-apiserver/pkg/apis/apiextensions/v1beta1"
	extclient "k8s.io/apiextensions-apiserver/pkg/client/clientset/clientset"
	apierrors "k8s.io/apimachinery/pkg/api/errors"
	"k8s.io/apimachinery/pkg/util/wait"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"os"
	"time"
	// Uncomment the following line to load the gcp plugin (only required to
	// authenticate against GKE clusters).
	_ "k8s.io/client-go/plugin/pkg/client/auth/gcp"

	crv1 "github.com/NervanaSystems/inferno-platform/server-controller/apis/cr/v1"
	"github.com/NervanaSystems/kube-controllers-go/pkg/controller"
	"github.com/NervanaSystems/kube-controllers-go/pkg/crd"
	"github.com/NervanaSystems/kube-controllers-go/pkg/resource"
	"github.com/NervanaSystems/kube-controllers-go/pkg/states"
	"github.com/NervanaSystems/kube-controllers-go/pkg/util"
)

func main() {
	kubeconfig := flag.String("kubeconfig", "", "Path to a kube config. Only required if out-of-cluster.")
	deploymentTemplateFile := flag.String("deploymentFile", "./resources/deployment.tmpl", "Path to a deployment file")
	serviceTemplateFile := flag.String("serviceFile", "./resources/service.tmpl", "Path to a service file")
	ingressTemplateFile := flag.String("ingressFile", "./resources/ingress.tmpl", "Path to an ingress file")
	platformDomain, ok := os.LookupEnv("PLATFORM_DOMAIN")
	if !ok {
		panic(errors.New("PLATFORM_DOMAIN environment variable not set. Controller was unable to start."))
	}
	servingImage, ok := os.LookupEnv("SERVING_IMAGE")
	if !ok {
		panic(errors.New("SERVING_IMAGE environment variable not set. Controller was unable to start."))
	}
	flag.Parse()
	// Create the client config. Use kubeconfig if given, otherwise assume
	// in-cluster.
	config, err := util.BuildConfig(*kubeconfig)
	if err != nil {
		panic(err)
	}

	clientset, err := extclient.NewForConfig(config)
	if err != nil {
		panic(err)
	}

	k8sclientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		panic(err)
	}

	// Create new CRD handle for the server resource type.
	crdHandle := crd.New(
		&crv1.Server{},
		&crv1.ServerList{},
		crv1.GroupName,
		crv1.Version,
		crv1.ServerResourceKind,
		crv1.ServerResourceSingular,
		crv1.ServerResourcePlural,
		extv1beta1.NamespaceScoped,
		"",
	)

	// Initialize custom resource using a CustomResourceDefinition if it does
	// not exist
	err = crd.WriteDefinition(clientset, crdHandle)
	if err != nil && !apierrors.IsAlreadyExists(err) {
		panic(err)
	}

	// NB: This is ONLY for the server controller. A CR's definition ought not
	// be deleted when a controller stops in a production environment.
	defer crd.DeleteDefinition(clientset, crdHandle)

	// Make a new config for our extension's API group, using the first config
	// as a baseline
	crdClient, err := crd.NewClient(*config, crdHandle)
	if err != nil {
		panic(err)
	}

	globalTemplateValues := resource.GlobalTemplateValues{}
	globalTemplateValues["platformDomain"] = platformDomain
	globalTemplateValues["servingImage"] = servingImage
	deploymentClient := resource.NewDeploymentClient(globalTemplateValues, k8sclientset, *deploymentTemplateFile)
	serviceClient := resource.NewServiceClient(globalTemplateValues, k8sclientset, *serviceTemplateFile)
	ingressClient := resource.NewIngressClient(globalTemplateValues, k8sclientset, *ingressTemplateFile)

	// Start a controller for instances of our custom resource.
	hooks := serverHooks{crdClient, deploymentClient, serviceClient, ingressClient}
	controller := controller.New(crdHandle, &hooks, crdClient.RESTClient())

	ctx, cancelFunc := context.WithCancel(context.Background())
	defer cancelFunc()
	go controller.Run(ctx, apiv1.NamespaceAll)

	<-ctx.Done()
}

func waitForServerInstanceProcessed(crdClient rest.Interface, name string) error {
	return wait.Poll(100*time.Millisecond, 10*time.Second, func() (bool, error) {
		var server crv1.Server
		err := crdClient.Get().
			Resource(crv1.ServerResourcePlural).
			Namespace(apiv1.NamespaceDefault).
			Name(name).
			Do().Into(&server)

		if err == nil && server.Status.State == states.Completed {
			return true, nil
		}

		return false, err
	})
}
