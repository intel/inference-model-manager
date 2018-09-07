package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"html/template"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"path/filepath"
	"reflect"
	"strings"

	crv1 "github.com/NervanaSystems/inferno-platform/server-controller/apis/cr/v1"
	"github.com/NervanaSystems/kube-controllers-go/pkg/crd"
	"github.com/NervanaSystems/kube-controllers-go/pkg/resource"
	"github.com/NervanaSystems/kube-controllers-go/pkg/states"
)

// serverHooks implements controller.Hooks.
type serverHooks struct {
	crdClient        crd.Client
	deploymentClient resource.Client
	serviceClient    resource.Client
	ingressClient    resource.Client
	replicaPath      string
	argPath          string
	resourcePath     string
}

type patchData struct {
	Replicas      int
	ModelName     string
	ModelVersion  int
	Namespace     string
	ResourcePath  string
	ResourceValue string
	MethodType    string
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

func (c *serverHooks) Add(obj interface{}) {
	server := obj.(*crv1.Server)
	fmt.Printf("[CONTROLLER] OnAdd %s\n", server)
	// NEVER modify objects from the store. It's a read-only, local cache.
	// You can use DeepCopy() to make a deep copy of original object and modify
	// this copy or create a copy manually for better performance.

	serverCopy := server.DeepCopy()
	ownerRef := metav1.NewControllerRef(server, crv1.GVK)
	err := c.deploymentClient.Create(serverCopy.Namespace(), struct {
		*crv1.Server
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
		*crv1.Server
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
		*crv1.Server
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

	serverCopy.Status = crv1.ServerStatus{
		State:   states.Completed,
		Message: "Successfully processed by controller",
	}
}

func (c *serverHooks) Update(oldObj, newObj interface{}) {
	oldServer := oldObj.(*crv1.Server)
	newServer := newObj.(*crv1.Server)
	fmt.Printf("[CONTROLLER] OnUpdate\n")
	fmt.Printf("New Server %s\n", newServer)
	fmt.Printf("Old Server %s\n", oldServer)
	var stringPatch []patchStructString
	var intPatch []patchStructInt
	p := patchData{Replicas: newServer.Spec.Replicas, ModelName: newServer.Spec.ModelName, ModelVersion: newServer.Spec.ModelVersion, Namespace: oldServer.Namespace()}
	fmt.Printf("Check resource field.\n")
	stringPatch, err := prepareJsonPatchStrings(c.resourcePath, "limits", stringPatch, oldServer.Spec.Resources.Limits, newServer.Spec.Resources.Limits, p)
	if err != nil {
		fmt.Printf("ERROR during resource/limits changes preparation: %v\n", err)
		return
	}
	stringPatch, err = prepareJsonPatchStrings(c.resourcePath, "requests", stringPatch, oldServer.Spec.Resources.Requests, newServer.Spec.Resources.Requests, p)
	fmt.Printf("%s\n", stringPatch)
	if err != nil {
		fmt.Printf("ERROR during resource/requests changes preparation: %v\n", err)
		return
	}

	fmt.Printf("Check replica field\n")
	if oldServer.Spec.Replicas != newServer.Spec.Replicas && newServer.Spec.Replicas >= 0 {
		var replicaPatch patchStructInt
		err := getPatchStructInt(c.replicaPath, p, &replicaPatch)
		if err != nil {
			fmt.Printf("ERROR during replica patch preparation: %v\n", err)
			return
		}
		intPatch = append(intPatch, replicaPatch)

	}
	fmt.Printf("Check ModelName and ModelVersion fields.\n")
	if oldServer.Spec.ModelName != newServer.Spec.ModelName || oldServer.Spec.ModelVersion != newServer.Spec.ModelVersion {
		var argPatch patchStructString
		err := getPatchStructString(c.argPath, p, &argPatch)
		if err != nil {
			fmt.Printf("ERROR during modelName and modelVersion patch preparation: %v\n", err)
			return
		}
		stringPatch = append(stringPatch, argPatch)
	}
	if len(stringPatch) > 0 {
		fmt.Printf("Will try to update server.\n")
		patchBytes, err := json.Marshal(stringPatch)
		fmt.Printf("JsonPatch %s\n", string(patchBytes))
		if err != nil {
			fmt.Printf("ERROR during preparing JsonPatch %v\n", err.Error())
			return
		}

		err = c.deploymentClient.Update(oldServer.Namespace(), oldServer.Spec.EndpointName, patchBytes)
		if err != nil {
			fmt.Printf("ERROR during making server patching%v\n", err)
			return
		}
		fmt.Printf("Updating succeeded for the server %v\n", oldServer.ObjectMeta.SelfLink)
	}

	if len(intPatch) > 0 {
		fmt.Printf("Will try to scale server.\n")
		patchIntBytes, err := json.Marshal(intPatch)
		fmt.Printf("Scale JsonPatch %s\n", string(patchIntBytes))
		if err != nil {
			fmt.Printf("ERROR during preparing scale JsonPatch %v\n", err.Error())
			return
		}
		err = c.deploymentClient.Update(oldServer.Namespace(), oldServer.Spec.EndpointName, patchIntBytes)
		if err != nil {
			fmt.Printf("ERROR during making server replica patching %v\n", err)
			return
		}
		fmt.Printf("Scaling succeeded for the server %v\n", oldServer.ObjectMeta.SelfLink)
	}

}

func (c *serverHooks) Delete(obj interface{}) {
	server := obj.(*crv1.Server)
	fmt.Printf("[CONTROLLER] OnDelete %s\n", server.ObjectMeta.SelfLink)
}

func prepareJsonPatchStrings(resourceTmplPath string, resourceType string, stringPatch []patchStructString, oldData map[string]string, newData map[string]string, p patchData) ([]patchStructString, error) {
	eq := reflect.DeepEqual(newData, oldData)
	if !eq {
		fmt.Printf("%s are unequal.\n", resourceType)
		oldMemoryVal, oldMemoryOK := oldData["memory"]
		oldCpuVal, oldCpuOK := oldData["cpu"]

		memoryValue, memoryOK := newData["memory"]
		cpuValue, cpuOK := newData["cpu"]
		cpuPathList := []string{resourceType, "cpu"}
		memoryPathList := []string{resourceType, "memory"}

		cpuPath := strings.Join(cpuPathList, "/")
		memoryPath := strings.Join(memoryPathList, "/")

		cpuPatchLine, err := createResourcePatch(resourceTmplPath, cpuPath, oldCpuVal, cpuValue, oldCpuOK, cpuOK, p)
		if err == nil && !(!oldCpuOK && !cpuOK) {
			stringPatch = append(stringPatch, cpuPatchLine)
		} else if err != nil {
			return nil, err
		}

		memoryPatchLine, err := createResourcePatch(resourceTmplPath, memoryPath, oldMemoryVal, memoryValue, oldMemoryOK, memoryOK, p)
		if err == nil && !(!oldMemoryOK && !memoryOK) {
			stringPatch = append(stringPatch, memoryPatchLine)
		} else if err != nil {
			return nil, err
		}
	}
	fmt.Printf("Changesmap %s\n", stringPatch)
	return stringPatch, nil

}

func createResourcePatch(resourceTmplPath string, resourcePath string, oldValue string, newValue string, oldKeyOK bool, newKeyOK bool, p patchData) (patchStructString, error) {
	var newPatchLine patchStructString
	p.ResourcePath = resourcePath
	if !oldKeyOK && !newKeyOK {
		return newPatchLine, nil
	}

	if oldKeyOK && !newKeyOK {
		p.MethodType = "remove"
	} else if !oldKeyOK && newKeyOK {
		p.ResourceValue = newValue
		p.MethodType = "add"
	} else if (oldKeyOK && newKeyOK) && (oldValue != newValue) {
		p.ResourceValue = newValue
		p.MethodType = "replace"
	}
	err := getPatchStructString(resourceTmplPath, p, &newPatchLine)
	return newPatchLine, err
}

func fillPatchTemplate(templateFileName string, data patchData) ([]byte, error) {
	baseFileName := filepath.Base(templateFileName)
	tmpl := template.New(baseFileName)
	tmpl, err := tmpl.ParseFiles(templateFileName)
	if err != nil {
		return nil, err
	}
	var buf bytes.Buffer
	err = tmpl.Execute(&buf, data)
	if err != nil {
		return nil, err
	}
	return buf.Bytes(), err
}

func getPatchStructString(templateFileName string, pdata patchData, dataPatch *patchStructString) error {
	data, err := fillPatchTemplate(templateFileName, pdata)
	if err != nil {
		return err
	}
	fmt.Printf("Struct with string %s\n", data)
	err = json.Unmarshal(data, &dataPatch)
	if err != nil {
		return err
	}
	return nil
}

func getPatchStructInt(templateFileName string, pdata patchData, dataPatch *patchStructInt) error {
	data, err := fillPatchTemplate(templateFileName, pdata)
	if err != nil {
		return err
	}
	fmt.Printf("Struct with int %s\n", data)
	err = json.Unmarshal(data, &dataPatch)
	if err != nil {
		return err
	}
	return nil
}
