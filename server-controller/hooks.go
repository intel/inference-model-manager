//
// Copyright (c) 2018-2019 Intel Corporation
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
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"log"
	"reflect"
	"strings"
	"text/template"
	"time"

	crv1 "github.com/IntelAI/inference-model-manager/server-controller/apis/cr/v1"
	"github.com/intel/crd-reconciler-for-kubernetes/pkg/resource"
	"github.com/intel/crd-reconciler-for-kubernetes/pkg/states"
)

type templateClients struct {
	deploymentClient resource.Client
	serviceClient    resource.Client
	ingressClient    resource.Client
	configMapClient  resource.Client
}

// serverHooks implements controller.Hooks.
type serverHooks struct {
	templates map[string]templateClients
}

type patchData struct {
	ModelName          string
	ModelVersionPolicy string
	Namespace          string
	ResourcePath       string
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

var subjectNamePath = "/metadata/annotations/allowed-values"
var replicaPath = "/spec/replicas"
var resourcePath = "/spec/template/spec/containers/0/resources/{{.ResourcePath}}"
var configRollingPath = "/spec/template/metadata/labels/configDate"

func (c *serverHooks) Add(obj interface{}) {
	server := obj.(*crv1.InferenceEndpoint)
	log.Printf("[CONTROLLER] OnAdd %s\n", server.ObjectMeta.SelfLink)
	// NEVER modify objects from the store. It's a read-only, local cache.
	// You can use DeepCopy() to make a deep copy of original object and modify
	// this copy or create a copy manually for better performance.

	serverCopy := server.DeepCopy()
	ownerRef := metav1.NewControllerRef(server, crv1.GVK)
	servingName := serverCopy.Spec.TemplateName
	if _, ok := c.templates[servingName]; !ok {
		log.Printf("There is no such template: %s\n", servingName)
		return
	}

	err := c.templates[servingName].configMapClient.Create(serverCopy.Namespace(), struct {
		*crv1.InferenceEndpoint
		metav1.OwnerReference
	}{
		serverCopy,
		*ownerRef,
	})

	if err != nil {
		log.Printf("ERROR during configMap creation: %v\n", err)
		return
	}
	log.Printf("ConfigMap (%s) created successfully\n", serverCopy.Spec.EndpointName)

	err = c.templates[servingName].deploymentClient.Create(serverCopy.Namespace(), struct {
		*crv1.InferenceEndpoint
		metav1.OwnerReference
	}{
		serverCopy,
		*ownerRef,
	})

	if err != nil {
		log.Printf("ERROR during deployment creation: %v\n", err)
		return
	}
	log.Printf("Deployment (%s) created successfully\n", serverCopy.Spec.EndpointName)
	// Patch below is required to create special label for triggering new deployments after configmap change
	err = c.addConfigDateToDeploy(servingName, serverCopy)
	if err != nil {
		log.Printf("ERROR during adding configDate label to deployment: %v\n", err)
		return
	}

	err = c.templates[servingName].serviceClient.Create(serverCopy.Namespace(), struct {
		*crv1.InferenceEndpoint
		metav1.OwnerReference
	}{
		serverCopy,
		*ownerRef,
	})

	if err != nil {
		log.Printf("ERROR during service creation: %v\n", err)
		return
	}
	log.Printf("Service (%s) created successfully\n", serverCopy.Spec.EndpointName)

	err = c.templates[servingName].ingressClient.Create(serverCopy.Namespace(), struct {
		*crv1.InferenceEndpoint
		metav1.OwnerReference
	}{
		serverCopy,
		*ownerRef,
	})

	if err != nil {
		log.Printf("ERROR during ingress creation: %v\n", err)
		return
	}
	log.Printf("Ingress (%s) created successfully\n", serverCopy.Spec.EndpointName)

	serverCopy.Status = crv1.InferenceEndpointStatus{
		State:   states.Completed,
		Message: "Successfully processed by controller",
	}
}

func (c *serverHooks) Update(oldObj, newObj interface{}) {
	oldServer := oldObj.(*crv1.InferenceEndpoint)
	newServer := newObj.(*crv1.InferenceEndpoint)
	log.Printf("[CONTROLLER] OnUpdate\n")
	log.Printf("New Server %s\n", newServer.ObjectMeta.SelfLink)
	log.Printf("Old Server %s\n", oldServer.ObjectMeta.SelfLink)
	var err error
	servingName := newServer.Spec.TemplateName
	if oldServer.Spec.TemplateName != newServer.Spec.TemplateName {
		if _, ok := c.templates[servingName]; !ok {
			log.Printf("There is no such template: %s\n", servingName)
			return
		}
		c.updateTemplate(oldServer, newServer)
		log.Printf("Updating succeeded for the server %v\n", oldServer.ObjectMeta.SelfLink)
		return
	}
	deploymentPatchLines := make([]interface{}, 0)
	ingressPatchLines := make([]interface{}, 0)

	p := patchData{ModelName: newServer.Spec.ModelName, ModelVersionPolicy: newServer.Spec.ModelVersionPolicy, Namespace: oldServer.Namespace()}
	log.Printf("Check resource field.\n")
	deploymentPatchLines, err = prepareJSONPatchFromMap("limits", deploymentPatchLines, oldServer.Spec.Resources.Limits, newServer.Spec.Resources.Limits, p)
	if err != nil {
		log.Printf("ERROR during resource/limits changes preparation: %v\n", err)
		return
	}
	deploymentPatchLines, err = prepareJSONPatchFromMap("requests", deploymentPatchLines, oldServer.Spec.Resources.Requests, newServer.Spec.Resources.Requests, p)
	if err != nil {
		log.Printf("ERROR during resource/requests changes preparation: %v\n", err)
		return
	}

	log.Printf("Check replica field\n")
	if oldServer.Spec.Replicas != newServer.Spec.Replicas && newServer.Spec.Replicas >= 0 {
		replicaPatch := patchStructInt{Op: "replace", Path: replicaPath, Value: newServer.Spec.Replicas}
		deploymentPatchLines = append(deploymentPatchLines, replicaPatch)

	}

	log.Printf("Check subjectName field\n")
	if oldServer.Spec.SubjectName != newServer.Spec.SubjectName {
		annotationParts := []string{"CN", newServer.Spec.SubjectName}
		annotation := strings.Join(annotationParts, "=")
		subjectNamePatch := patchStructString{Op: "replace", Path: subjectNamePath, Value: annotation}
		ingressPatchLines = append(ingressPatchLines, subjectNamePatch)
	}

	log.Printf("Check ModelName and ModelVersionPolicy fields.\n")
	if oldServer.Spec.ModelName != newServer.Spec.ModelName ||
		oldServer.Spec.ModelVersionPolicy != newServer.Spec.ModelVersionPolicy {
		ownerRef := metav1.NewControllerRef(oldServer, crv1.GVK)
		err := c.templates[servingName].configMapClient.Update(oldServer.Namespace(), oldServer.Spec.EndpointName, struct {
			*crv1.InferenceEndpoint
			metav1.OwnerReference
		}{
			newServer,
			*ownerRef,
		})

		if err != nil {
			log.Printf("ERROR during configMap update: %v\n", err)
			return
		}
		log.Printf("ConfigMap (%s) updated successfully\n", newServer.Spec.EndpointName)
		// Necessary patch to trigger new deployment after configmap change
		t := time.Now().UTC()
		configMapPatch := patchStructString{Op: "replace", Path: configRollingPath, Value: t.Format("20060102150405")}
		deploymentPatchLines = append(deploymentPatchLines, configMapPatch)
	}

	if len(deploymentPatchLines) == 0 && len(ingressPatchLines) == 0 {
		log.Printf("Update not required. No changes detected\n")
		return
	}

	if len(deploymentPatchLines) > 0 {
		log.Printf("Will try to update deployment.\n")
		patchBytes, err := json.Marshal(deploymentPatchLines)
		if err != nil {
			log.Printf("ERROR during preparing bytes to send %v\n", err.Error())
			return
		}
		log.Printf("JsonPatch which will be applied: %s\n", string(patchBytes))
		err = c.templates[servingName].deploymentClient.Patch(oldServer.Namespace(), oldServer.Spec.EndpointName, patchBytes)
		if err != nil {
			log.Printf("ERROR during update operation %v\n", err.Error())
			return
		}

	}

	if len(ingressPatchLines) > 0 {
		log.Printf("Will try to update ingress.\n")
		patchBytes, err := json.Marshal(ingressPatchLines)
		if err != nil {
			log.Printf("ERROR during preparing bytes to send %v\n", err.Error())
			return
		}
		log.Printf("JsonPatch which will be applied: %s\n", string(patchBytes))
		err = c.templates[servingName].ingressClient.Patch(oldServer.Namespace(), oldServer.Spec.EndpointName, patchBytes)
		if err != nil {
			log.Printf("ERROR during update operation %v\n", err.Error())
			return
		}
	}
	log.Printf("Server %v updated successfully\n", oldServer.ObjectMeta.SelfLink)
}

func (c *serverHooks) Delete(obj interface{}) {
	server := obj.(*crv1.InferenceEndpoint)
	log.Printf("[CONTROLLER] OnDelete %s\n", server.ObjectMeta.SelfLink)
}

func (c *serverHooks) addConfigDateToDeploy(servingName string, obj interface{}) error {
	server := obj.(*crv1.InferenceEndpoint)
	log.Printf("A special label for deployment 'configDate' will be added.\n")
	t := time.Now().UTC()
	configMapPatch := []patchStructString{{Op: "add", Path: configRollingPath, Value: t.Format("20060102150405")}}
	patchBytes, err := json.Marshal(configMapPatch)
	if err != nil {
		log.Printf("ERROR during preparing bytes to send %v\n", err.Error())
		return err
	}
	log.Printf("JsonPatch which will be applied: %s\n", string(patchBytes))
	err = c.templates[servingName].deploymentClient.Patch(server.Namespace(), server.Spec.EndpointName, patchBytes)
	if err != nil {
		log.Printf("ERROR during patch operation %v\n", err.Error())
		log.Printf("Object updates will not be available.\n")
		return err
	}
	return nil
}

func (c *serverHooks) updateTemplate(oldObj, newObj interface{}) {
	oldServer := oldObj.(*crv1.InferenceEndpoint)
	newServer := newObj.(*crv1.InferenceEndpoint)
	ownerRef := metav1.NewControllerRef(oldServer, crv1.GVK)
	servingName := oldServer.Spec.TemplateName
	if _, ok := c.templates[servingName]; !ok {
		log.Printf("There is no such template: %s\n", servingName)
		return
	}

	err := c.templates[servingName].configMapClient.Update(oldServer.Namespace(), oldServer.Spec.EndpointName, struct {
		*crv1.InferenceEndpoint
		metav1.OwnerReference
	}{
		newServer,
		*ownerRef,
	})

	if err != nil {
		log.Printf("ERROR during configMap update: %v\n", err)
		return
	}
	log.Printf("ConfigMap (%s) updated successfully\n", oldServer.Spec.EndpointName)

	err = c.templates[servingName].deploymentClient.Update(oldServer.Namespace(), oldServer.Spec.EndpointName, struct {
		*crv1.InferenceEndpoint
		metav1.OwnerReference
	}{
		newServer,
		*ownerRef,
	})

	if err != nil {
		log.Printf("ERROR during deployment update: %v\n", err)
		return
	}
	log.Printf("Deployment (%s) updated successfully\n", oldServer.Spec.EndpointName)
	// Patch below is required to create special label for triggering new deployments after configmap change
	err = c.addConfigDateToDeploy(servingName, newServer)
	if err != nil {
		log.Printf("ERROR during adding configDate label to deployment: %v\n", err)
		return
	}

	err = c.templates[servingName].serviceClient.Delete(oldServer.Namespace(), oldServer.Spec.EndpointName)
	if err != nil {
		log.Printf("ERROR during service delete: %v\n", err)
		return
	}
	log.Printf("Service (%s) deleted successfully\n", oldServer.Spec.EndpointName)
	err = c.templates[servingName].serviceClient.Create(oldServer.Namespace(), struct {
		*crv1.InferenceEndpoint
		metav1.OwnerReference
	}{
		newServer,
		*ownerRef,
	})

	if err != nil {
		log.Printf("ERROR during service create: %v\n", err)
		return
	}
	log.Printf("Service (%s) created successfully\n", oldServer.Spec.EndpointName)

	err = c.templates[servingName].ingressClient.Update(oldServer.Namespace(), oldServer.Spec.EndpointName, struct {
		*crv1.InferenceEndpoint
		metav1.OwnerReference
	}{
		newServer,
		*ownerRef,
	})

	if err != nil {
		log.Printf("ERROR during ingress update: %v\n", err)
		return
	}
	log.Printf("Ingress (%s) updated successfully\n", oldServer.Spec.EndpointName)
}

func prepareJSONPatchFromMap(resourceType string, mapPatch []interface{}, oldData map[string]string, newData map[string]string, p patchData) ([]interface{}, error) {
	eq := reflect.DeepEqual(newData, oldData)
	if !eq {
		log.Printf("%s are unequal.\n", resourceType)
		p.ResourcePath = resourceType
		resourcePath, err := fillTemplate(resourcePath, p)
		if err != nil {
			return nil, err
		}
		_, oldMemoryOK := oldData["memory"]
		_, oldCPUOK := oldData["cpu"]

		memoryValue, memoryOK := newData["memory"]
		cpuValue, cpuOK := newData["cpu"]
		updateMap := make(map[string]string)
		var jsonPatchAction string
		if !memoryOK && !cpuOK && (oldCPUOK || oldMemoryOK) {
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
