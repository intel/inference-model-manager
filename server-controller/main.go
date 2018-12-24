//
// Copyright (c) 2018 Intel Corporation
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// SPDX-License-Identifier: EPL-2.0
//

// Note: the server only works with the code within the same release/branch.
package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"io/ioutil"
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

	crv1 "github.com/IntelAI/inference-model-manager/server-controller/apis/cr/v1"
	"github.com/intel/crd-reconciler-for-kubernetes/pkg/controller"
	"github.com/intel/crd-reconciler-for-kubernetes/pkg/crd"
	"github.com/intel/crd-reconciler-for-kubernetes/pkg/resource"
	"github.com/intel/crd-reconciler-for-kubernetes/pkg/states"
	"github.com/intel/crd-reconciler-for-kubernetes/pkg/util"
)

var templatesDir = "./resources"

func checkPath(path string) error {
	if _, err := os.Stat(templatesDir); err != nil {
		if os.IsNotExist(err) {
			err = errors.New(fmt.Sprintf("%s file does not exist.\n", path))
		} else {
			err = errors.New(fmt.Sprintf("Error occurred when checking %s directory existence %v\n", path, err))
		}
		return err
	}
	return nil
}

func prepareTemplateClients(templateName string, globalTemplateValues resource.GlobalTemplateValues, k8sclientset *kubernetes.Clientset) (templateClients, error) {
	k8sClients := templateClients{}
	templateFileDir := fmt.Sprintf("%s/%s", templatesDir, templateName)
	deploymentTemplateFileDir := fmt.Sprintf("%s/%s", templateFileDir, "deployment.tmpl")
	serviceTemplateFileDir := fmt.Sprintf("%s/%s", templateFileDir, "service.tmpl")
	ingressTemplateFileDir := fmt.Sprintf("%s/%s", templateFileDir, "ingress.tmpl")
	configMapTemplateFileDir := fmt.Sprintf("%s/%s", templateFileDir, "configMap.tmpl")

	err := checkPath(deploymentTemplateFileDir)
	if err != nil {
		return k8sClients, err
	}
	deploymentClient := resource.NewDeploymentClient(globalTemplateValues, k8sclientset, deploymentTemplateFileDir)

	err = checkPath(serviceTemplateFileDir)
	if err != nil {
		return k8sClients, err
	}
	serviceClient := resource.NewServiceClient(globalTemplateValues, k8sclientset, serviceTemplateFileDir)

	err = checkPath(ingressTemplateFileDir)
	if err != nil {
		return k8sClients, err
	}
	ingressClient := resource.NewIngressClient(globalTemplateValues, k8sclientset, ingressTemplateFileDir)

	err = checkPath(configMapTemplateFileDir)
	if err != nil {
		return k8sClients, err
	}
	configMapClient := resource.NewConfigMapClient(globalTemplateValues, k8sclientset, configMapTemplateFileDir)

	k8sClients = templateClients{deploymentClient, serviceClient, ingressClient, configMapClient}

	return k8sClients, nil

}
func main() {
	kubeconfig := flag.String("kubeconfig", "", "Path to a kube config. Only required if out-of-cluster.")
	platformDomain, ok := os.LookupEnv("PLATFORM_DOMAIN")
	if !ok {
		panic(errors.New("PLATFORM_DOMAIN environment variable not set. Controller was unable to start.\n"))
	}
	s3UseHTTPS, ok := os.LookupEnv("S3_USE_HTTPS")
	if !ok {
		panic(errors.New("S3_USE_HTTPS environment variable not set. Controller was unable to start.\n"))
	}
	s3VerifySsl, ok := os.LookupEnv("S3_VERIFY_SSL")
	if !ok {
		panic(errors.New("S3_VERIFY_SSL environment variable not set. Controller was unable to start.\n"))
	}
	if _, err := os.Stat(templatesDir); err != nil {
		if os.IsNotExist(err) {
			specialErrorMessage := fmt.Sprintf("%s directory does not exist\n", templatesDir)
			panic(errors.New(specialErrorMessage))
		} else {
			specialErrorMessage := fmt.Sprintf("Error occurred when checking %s directory existence %v\n", templatesDir, err)
			panic(errors.New(specialErrorMessage))
		}
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
		&crv1.InferenceEndpoint{},
		&crv1.InferenceEndpointList{},
		crv1.GroupName,
		crv1.Version,
		crv1.InferenceEndpointResourceKind,
		crv1.InferenceEndpointResourceSingular,
		crv1.InferenceEndpointResourcePlural,
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
	globalTemplateValues["s3UseHttps"] = s3UseHTTPS
	globalTemplateValues["s3VerifySsl"] = s3VerifySsl
	files, err := ioutil.ReadDir(templatesDir)
	if err != nil {
		specialErrorMessage := fmt.Sprintf("Problem with reading %s directory\n", templatesDir)
		panic(errors.New(specialErrorMessage))
	}
	updateMap := make(map[string]templateClients)
	for _, f := range files {
		templateClients, err := prepareTemplateClients(f.Name(), globalTemplateValues, k8sclientset)
		if err != nil {
			fmt.Printf("Cannot create clients for templates: %s", f.Name())
		} else {
			updateMap[f.Name()] = templateClients
		}
	}

	// Start a controller for instances of our custom resource.
	hooks := serverHooks{updateMap}
	controller := controller.New(crdHandle, &hooks, crdClient.RESTClient())

	ctx, cancelFunc := context.WithCancel(context.Background())
	defer cancelFunc()
	go controller.Run(ctx, apiv1.NamespaceAll)

	<-ctx.Done()
}

func waitForServerInstanceProcessed(crdClient rest.Interface, name string) error {
	return wait.Poll(100*time.Millisecond, 10*time.Second, func() (bool, error) {
		var server crv1.InferenceEndpoint
		err := crdClient.Get().
			Resource(crv1.InferenceEndpointResourcePlural).
			Namespace(apiv1.NamespaceDefault).
			Name(name).
			Do().Into(&server)

		if err == nil && server.Status.State == states.Completed {
			return true, nil
		}

		return false, err
	})
}
