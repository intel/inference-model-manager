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

package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"reflect"
	"text/template"

	crv1 "github.com/IntelAI/inference-model-manager/server-controller/apis/cr/v1"
	"github.com/intel/crd-reconciler-for-kubernetes/pkg/crd"
	"github.com/intel/crd-reconciler-for-kubernetes/pkg/resource"
	"github.com/intel/crd-reconciler-for-kubernetes/pkg/states"
)

// serverHooks implements controller.Hooks.
type serverHooks struct {
	crdClient        crd.Client
	deploymentClient resource.Client
	serviceClient    resource.Client
	ingressClient    resource.Client
}

type patchData struct {
	ModelName    string
	ModelVersion int
	Namespace    string
	ResourcePath string
}

type patchStructInt struct {
	Op    string `json:"op"`
	Path  string `json:"path"`
	Value int    `json:"value"`
}

type patchStructString struct {
	Op    string `json:"op"`
	Path  string `json:"path"`
	Value string `json:"value"`
}

type patchStructMap struct {
	Op    string            `json:"op"`
	Path  string            `json:"path"`
	Value map[string]string `json:"value"`
}

var replicaPath = "/spec/replicas"
var argPath = "/spec/template/spec/containers/0/args/0"
var resourcePath = "/spec/template/spec/containers/0/resources/{{.ResourcePath}}"
var argValue = "tensorflow_model_server --port=9000 --model_name={{.ModelName}} --model_base_path=s3://{{.Namespace}}/{{.ModelName}}-{{.ModelVersion}}"

func (c *serverHooks) Add(obj interface{}) {
	server := obj.(*crv1.InferenceEndpoint)
	fmt.Printf("[CONTROLLER] OnAdd %s\n", server)
	// NEVER modify objects from the store. It's a read-only, local cache.
	// You can use DeepCopy() to make a deep copy of original object and modify
	// this copy or create a copy manually for better performance.

	serverCopy := server.DeepCopy()
	ownerRef := metav1.NewControllerRef(server, crv1.GVK)
	err := c.deploymentClient.Create(serverCopy.Namespace(), struct {
		*crv1.InferenceEndpoint
		metav1.OwnerReference
	}{
		serverCopy,
		*ownerRef,
	})

	if err != nil {
		fmt.Printf("ERROR during deployment creation: %v\n", err)
		return
	}
	fmt.Printf("Deployment (%s) created successfully\n", serverCopy.Spec.EndpointName)

	err = c.serviceClient.Create(serverCopy.Namespace(), struct {
		*crv1.InferenceEndpoint
		metav1.OwnerReference
	}{
		serverCopy,
		*ownerRef,
	})

	if err != nil {
		fmt.Printf("ERROR during service creation: %v\n", err)
		return
	}
	fmt.Printf("Service (%s) created successfully\n", serverCopy.Spec.EndpointName)

	err = c.ingressClient.Create(serverCopy.Namespace(), struct {
		*crv1.InferenceEndpoint
		metav1.OwnerReference
	}{
		serverCopy,
		*ownerRef,
	})

	if err != nil {
		fmt.Printf("ERROR during ingress creation: %v\n", err)
		return
	}
	fmt.Printf("Ingress (%s) created successfully\n", serverCopy.Spec.EndpointName)

	serverCopy.Status = crv1.InferenceEndpointStatus{
		State:   states.Completed,
		Message: "Successfully processed by controller",
	}
}

func (c *serverHooks) Update(oldObj, newObj interface{}) {
	oldServer := oldObj.(*crv1.InferenceEndpoint)
	newServer := newObj.(*crv1.InferenceEndpoint)
	fmt.Printf("[CONTROLLER] OnUpdate\n")
	fmt.Printf("New Server %s\n", newServer)
	fmt.Printf("Old Server %s\n", oldServer)
	var err error
	patchLines := make([]interface{}, 0)
	p := patchData{ModelName: newServer.Spec.ModelName, ModelVersion: newServer.Spec.ModelVersion, Namespace: oldServer.Namespace()}
	fmt.Printf("Check resource field.\n")
	patchLines, err = prepareJsonPatchFromMap("limits", patchLines, oldServer.Spec.Resources.Limits, newServer.Spec.Resources.Limits, p)
	if err != nil {
		fmt.Printf("ERROR during resource/limits changes preparation: %v\n", err)
		return
	}
	patchLines, err = prepareJsonPatchFromMap("requests", patchLines, oldServer.Spec.Resources.Requests, newServer.Spec.Resources.Requests, p)
	if err != nil {
		fmt.Printf("ERROR during resource/requests changes preparation: %v\n", err)
		return
	}

	fmt.Printf("Check replica field\n")
	if oldServer.Spec.Replicas != newServer.Spec.Replicas && newServer.Spec.Replicas >= 0 {
		replicaPatch := patchStructInt{Op: "replace", Path: replicaPath, Value: newServer.Spec.Replicas}
		patchLines = append(patchLines, replicaPatch)

	}
	fmt.Printf("Check ModelName and ModelVersion fields.\n")
	if oldServer.Spec.ModelName != newServer.Spec.ModelName || oldServer.Spec.ModelVersion != newServer.Spec.ModelVersion {
		argValue, err := fillTemplate(argValue, p)
		if err != nil {
			fmt.Printf("ERROR during modelName and modelVersion patch preparation: %v\n", err)
			return
		}
		argPatch := patchStructString{Op: "replace", Path: argPath, Value: argValue}
		patchLines = append(patchLines, argPatch)
	}

	if len(patchLines) > 0 {
		fmt.Printf("Will try to update server.\n")
		patchBytes, err := json.Marshal(patchLines)
		if err != nil {
			fmt.Printf("ERROR during preparing bytes to send %v\n", err.Error())
			return
		}
		fmt.Printf("JsonPatch which will be applied: %s\n", string(patchBytes))
		err = c.deploymentClient.Update(oldServer.Namespace(), oldServer.Spec.EndpointName, patchBytes)
		if err != nil {
			fmt.Printf("ERROR during update operation %v\n", err.Error())
			return
		}

		fmt.Printf("Updating succeeded for the server %v\n", oldServer.ObjectMeta.SelfLink)
	}

}

func (c *serverHooks) Delete(obj interface{}) {
	server := obj.(*crv1.InferenceEndpoint)
	fmt.Printf("[CONTROLLER] OnDelete %s\n", server.ObjectMeta.SelfLink)
}

func prepareJsonPatchFromMap(resourceType string, mapPatch []interface{}, oldData map[string]string, newData map[string]string, p patchData) ([]interface{}, error) {
	eq := reflect.DeepEqual(newData, oldData)
	if !eq {
		fmt.Printf("%s are unequal.\n", resourceType)
		p.ResourcePath = resourceType
		resourcePath, err := fillTemplate(resourcePath, p)
		if err != nil {
			return nil, err
		}
		_, oldMemoryOK := oldData["memory"]
		_, oldCpuOK := oldData["cpu"]

		memoryValue, memoryOK := newData["memory"]
		cpuValue, cpuOK := newData["cpu"]
		updateMap := make(map[string]string)
		var jsonPatchAction string
		if !memoryOK && !cpuOK && (oldCpuOK || oldMemoryOK) {
			jsonPatchAction = "remove"
		} else {
			if cpuOK {
				updateMap["cpu"] = cpuValue
			}
			if memoryOK {
				updateMap["memory"] = memoryValue
			}
			jsonPatchAction = "add"
		}
		newMapStruct := patchStructMap{Op: jsonPatchAction, Path: resourcePath, Value: updateMap}
		mapPatch = append(mapPatch, newMapStruct)

	}
	return mapPatch, nil

}

func fillTemplate(templateToFill string, data patchData) (string, error) {
	tmpl := template.New("New")
	tmpl, err := tmpl.Parse(templateToFill)
	if err != nil {
		return "", err
	}
	var buf bytes.Buffer
	err = tmpl.Execute(&buf, data)
	if err != nil {
		return "", err
	}
	return buf.String(), err
}
