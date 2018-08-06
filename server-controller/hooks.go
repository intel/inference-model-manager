package main

import (
	"fmt"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

	crv1 "github.com/NervanaSystems/inferno-platform/server-controller/apis/cr/v1"
	"github.com/NervanaSystems/kube-controllers-go/pkg/crd"
	"github.com/NervanaSystems/kube-controllers-go/pkg/states"
	"github.com/NervanaSystems/kube-controllers-go/pkg/resource"
)

// serverHooks implements controller.Hooks.
type serverHooks struct {
	crdClient crd.Client
	deploymentClient resource.Client
	serviceClient resource.Client
	ingressClient resource.Client
}

func (c *serverHooks) Add(obj interface{}) {
	server := obj.(*crv1.Server)
	fmt.Printf("[CONTROLLER] OnAdd %s\n", server.ObjectMeta.SelfLink)
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
	} else {
		fmt.Printf("Deployment (%s-%d) created successfully\n",
			serverCopy.Spec.ModelName,
			serverCopy.Spec.ModelVersion)
	}

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
	} else {
		fmt.Printf("Service (%s-%d) created successfully\n",
			serverCopy.Spec.ModelName,
			serverCopy.Spec.ModelVersion)
	}


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
	} else {
		fmt.Printf("Ingress (%s-%d) created successfully\n",
			serverCopy.Spec.ModelName,
			serverCopy.Spec.ModelVersion)
	}

	serverCopy.Status = crv1.ServerStatus{
		State:   states.Completed,
		Message: "Successfully processed by controller",
	}

	_, err = c.crdClient.Update(serverCopy)
	if err != nil {
		fmt.Printf("ERROR updating status: %v\n", err)
	} else {
		fmt.Printf("UPDATED status: %#v\n", serverCopy)
	}
}

func (c *serverHooks) Update(oldObj, newObj interface{}) {
	oldServer := oldObj.(*crv1.Server)
	newServer := newObj.(*crv1.Server)
	fmt.Printf("[CONTROLLER] OnUpdate oldObj: %s\n", oldServer.ObjectMeta.SelfLink)
	fmt.Printf("[CONTROLLER] OnUpdate newObj: %s\n", newServer.ObjectMeta.SelfLink)
}

func (c *serverHooks) Delete(obj interface{}) {
	server := obj.(*crv1.Server)
	fmt.Printf("[CONTROLLER] OnDelete %s\n", server.ObjectMeta.SelfLink)
}
