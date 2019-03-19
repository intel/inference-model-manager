//
// Copyright (c) 2019 Intel Corporation
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//

package main

import (
	"bytes"
	"errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

	"log"
	"testing"

	crv1 "github.com/IntelAI/inference-model-manager/server-controller/apis/cr/v1"
	"os"
	"strings"
)

var (
	inferenceEndpoint = crv1.InferenceEndpoint{
		TypeMeta:   metav1.TypeMeta{},
		ObjectMeta: metav1.ObjectMeta{},
		Spec:       crv1.InferenceEndpointSpec{EndpointName: "test", TemplateName: "test"},
		Status:     crv1.InferenceEndpointStatus{}}

	inferenceEndpointEmpty = crv1.InferenceEndpoint{
		TypeMeta:   metav1.TypeMeta{},
		ObjectMeta: metav1.ObjectMeta{},
		Spec:       crv1.InferenceEndpointSpec{},
		Status:     crv1.InferenceEndpointStatus{}}
)

type clientErr struct {
	configMapError        error
	deploymentClientError error
	serviceClientError    error
	ingressClientError    error
}

var inferenceEndpointsTestAdd = []struct {
	name              string
	inferenceEndpoint crv1.InferenceEndpoint
	expected          string
	clientErrors      clientErr
}{
	{
		name:              "No template provided",
		inferenceEndpoint: inferenceEndpointEmpty,
		expected:          "There is no such template",
		clientErrors:      clientErr{nil, nil, nil, nil}},
	{
		name:              "Success to create template",
		inferenceEndpoint: inferenceEndpoint,
		expected:          "created successfully",
		clientErrors:      clientErr{nil, nil, nil, nil}},
	{
		name:              "Config map creation error",
		inferenceEndpoint: inferenceEndpoint,
		expected:          "ERROR during configMap creation",
		clientErrors:      clientErr{errors.New(""), nil, nil, nil}},
	{
		name:              "Deployment creation error",
		inferenceEndpoint: inferenceEndpoint,
		expected:          "ERROR during deployment creation",
		clientErrors:      clientErr{nil, errors.New(""), nil, nil}},
	{
		name:              "Service creation error",
		inferenceEndpoint: inferenceEndpoint,
		expected:          "ERROR during service creation",
		clientErrors:      clientErr{nil, nil, errors.New(""), nil}},
	{
		name:              "Ingress creation error",
		inferenceEndpoint: inferenceEndpoint,
		expected:          "ERROR during ingress creation",
		clientErrors:      clientErr{nil, nil, nil, errors.New("")}},
}

func testAdd(infer crv1.InferenceEndpoint, errs clientErr) string {
	var buf bytes.Buffer
	log.SetOutput(&buf)
	defer func() {
		log.SetOutput(os.Stderr)
	}()

	updateMap := make(map[string]templateClients)
	configMapClient := newMockClient(errs.configMapError)
	deploymentClient := newMockClient(errs.deploymentClientError)
	serviceClient := newMockClient(errs.serviceClientError)
	ingressClient := newMockClient(errs.ingressClientError)
	k8sClients := templateClients{deploymentClient, serviceClient, ingressClient, configMapClient}
	updateMap["test"] = k8sClients
	hooks := serverHooks{updateMap}
	inferenceEndpoint := infer
	hooks.Add(&inferenceEndpoint)
	return buf.String()
}

var inferenceEndpointsTestUpdateTemplate = []struct {
	name         string
	oldServer    crv1.InferenceEndpoint
	newServer    crv1.InferenceEndpoint
	expected     string
	clientErrors clientErr
}{
	{
		name:         "No such template",
		oldServer:    inferenceEndpointEmpty,
		newServer:    inferenceEndpoint,
		expected:     "There is no such template",
		clientErrors: clientErr{nil, nil, nil, nil}},
	{
		name:         "Success to update template",
		oldServer:    inferenceEndpoint,
		newServer:    inferenceEndpoint,
		expected:     "updated successfully",
		clientErrors: clientErr{nil, nil, nil, nil}},
	{
		name:         "Config map update error",
		oldServer:    inferenceEndpoint,
		newServer:    inferenceEndpoint,
		expected:     "ERROR during configMap update",
		clientErrors: clientErr{errors.New(""), nil, nil, nil}},
	{
		name:         "Deployment update error",
		oldServer:    inferenceEndpoint,
		newServer:    inferenceEndpoint,
		expected:     "ERROR during deployment update",
		clientErrors: clientErr{nil, errors.New(""), nil, nil}},
	{
		name:         "Service creation error",
		oldServer:    inferenceEndpoint,
		newServer:    inferenceEndpoint,
		expected:     "ERROR during service create",
		clientErrors: clientErr{nil, nil, errors.New(""), nil}},
	{
		name:         "Ingress update error",
		oldServer:    inferenceEndpoint,
		newServer:    inferenceEndpoint,
		expected:     "ERROR during ingress update",
		clientErrors: clientErr{nil, nil, nil, errors.New("")}},
}

func testUpdateTemplate(oldServer, newServer crv1.InferenceEndpoint, errs clientErr) string {
	var buf bytes.Buffer
	log.SetOutput(&buf)
	defer func() {
		log.SetOutput(os.Stderr)
	}()
	updateMap := make(map[string]templateClients)
	configMapClient := newMockClient(errs.configMapError)
	deploymentClient := newMockClient(errs.deploymentClientError)
	serviceClient := newMockClient(errs.serviceClientError)
	ingressClient := newMockClient(errs.ingressClientError)
	k8sClients := templateClients{deploymentClient, serviceClient, ingressClient, configMapClient}
	updateMap["test"] = k8sClients
	hooks := serverHooks{updateMap}
	oldInferenceEndpoint := oldServer
	newInferenceEndpoint := newServer
	hooks.updateTemplate(&oldInferenceEndpoint, &newInferenceEndpoint)
	return buf.String()
}

func TestAdd(t *testing.T) {
	for _, tt := range inferenceEndpointsTestAdd {
		t.Run(tt.name, func(t *testing.T) {
			got := testAdd(tt.inferenceEndpoint, tt.clientErrors)
			if !strings.Contains(got, tt.expected) {
				t.Logf("Expected: (%s), got: (%s)\n", tt.expected, got)
				t.Fail()
			}
		})
	}
}

func TestUpdateTemplate(t *testing.T) {
	for _, tt := range inferenceEndpointsTestUpdateTemplate {
		t.Run(tt.name, func(t *testing.T) {
			got := testUpdateTemplate(tt.oldServer, tt.newServer, tt.clientErrors)
			if !strings.Contains(got, tt.expected) {
				t.Logf("Expected: (%s), got: (%s)\n", tt.expected, got)
				t.Fail()
			}
		})
	}
}
