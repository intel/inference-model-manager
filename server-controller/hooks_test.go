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
	"text/template"
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

type clientError struct {
	configMapError             error
	deploymentClientError      error
	deploymentClientPatchError error
	serviceClientError         error
	ingressClientError         error
	ingressClientPatchError    error
}

var nilClientError = clientError{
	configMapError:             nil,
	deploymentClientError:      nil,
	deploymentClientPatchError: nil,
	serviceClientError:         nil,
	ingressClientError:         nil,
	ingressClientPatchError:    nil,
}

func createTemplateClients(errs clientError) map[string]templateClients {
	updateMap := make(map[string]templateClients)
	configMapClient := newMockClient(errs.configMapError, nil)
	deploymentClient := newMockClient(errs.deploymentClientError, errs.deploymentClientPatchError)
	serviceClient := newMockClient(errs.serviceClientError, nil)
	ingressClient := newMockClient(errs.ingressClientError, errs.ingressClientPatchError)
	k8sClients := templateClients{deploymentClient, serviceClient, ingressClient, configMapClient}
	updateMap["test"] = k8sClients
	updateMap["exist"] = k8sClients
	return updateMap
}

var inferenceEndpointsTestAdd = []struct {
	name              string
	inferenceEndpoint crv1.InferenceEndpoint
	expected          string
	clientErrors      clientError
}{
	{
		name:              "No template provided",
		inferenceEndpoint: inferenceEndpointEmpty,
		expected:          "There is no such template",
		clientErrors:      nilClientError,
	},
	{
		name:              "Success to create template",
		inferenceEndpoint: inferenceEndpoint,
		expected:          "created successfully",
		clientErrors:      nilClientError,
	},
	{
		name:              "Config map creation error",
		inferenceEndpoint: inferenceEndpoint,
		expected:          "ERROR during configMap creation",
		clientErrors:      clientError{errors.New(""), nil, nil, nil, nil, nil},
	},
	{
		name:              "Deployment creation error",
		inferenceEndpoint: inferenceEndpoint,
		expected:          "ERROR during deployment creation",
		clientErrors:      clientError{nil, errors.New(""), nil, nil, nil, nil},
	},
	{
		name:              "Deployment patch error",
		inferenceEndpoint: inferenceEndpoint,
		expected:          "ERROR during adding configDate label to deployment",
		clientErrors:      clientError{nil, nil, errors.New(""), nil, nil, nil},
	},
	{
		name:              "Service creation error",
		inferenceEndpoint: inferenceEndpoint,
		expected:          "ERROR during service creation",
		clientErrors:      clientError{nil, nil, nil, errors.New(""), nil, nil},
	},
	{
		name:              "Ingress creation error",
		inferenceEndpoint: inferenceEndpoint,
		expected:          "ERROR during ingress creation",
		clientErrors:      clientError{nil, nil, nil, nil, errors.New(""), nil},
	},
}

func testAdd(infer crv1.InferenceEndpoint, errs clientError) string {
	var buf bytes.Buffer
	log.SetOutput(&buf)
	defer func() {
		log.SetOutput(os.Stderr)
	}()

	updateMap := createTemplateClients(errs)
	hooks := serverHooks{updateMap}
	inferenceEndpoint := infer
	hooks.Add(&inferenceEndpoint)
	return buf.String()
}

var inferenceEndpointsTestUpdate = []struct {
	name         string
	oldServer    crv1.InferenceEndpoint
	newServer    crv1.InferenceEndpoint
	expected     string
	clientErrors clientError
}{
	{
		name:      "No such template",
		oldServer: inferenceEndpoint,
		newServer: crv1.InferenceEndpoint{
			TypeMeta:   metav1.TypeMeta{},
			ObjectMeta: metav1.ObjectMeta{},
			Spec:       crv1.InferenceEndpointSpec{EndpointName: "test", TemplateName: "not_exist"},
			Status:     crv1.InferenceEndpointStatus{}},
		expected:     "There is no such template",
		clientErrors: nilClientError,
	},
	{
		name:      "Updating succeeded",
		oldServer: inferenceEndpoint,
		newServer: crv1.InferenceEndpoint{
			TypeMeta:   metav1.TypeMeta{},
			ObjectMeta: metav1.ObjectMeta{},
			Spec:       crv1.InferenceEndpointSpec{EndpointName: "test", TemplateName: "exist"},
			Status:     crv1.InferenceEndpointStatus{}},
		expected:     "Updating succeeded for the server",
		clientErrors: nilClientError,
	},
	{
		name:         "No changes detected",
		oldServer:    inferenceEndpoint,
		newServer:    inferenceEndpoint,
		expected:     "Update not required. No changes detected",
		clientErrors: nilClientError,
	},
	{
		name:      "SubjectName different",
		oldServer: inferenceEndpoint,
		newServer: crv1.InferenceEndpoint{
			TypeMeta:   metav1.TypeMeta{},
			ObjectMeta: metav1.ObjectMeta{},
			Spec:       crv1.InferenceEndpointSpec{EndpointName: "test", TemplateName: "test", SubjectName: "test"},
			Status:     crv1.InferenceEndpointStatus{}},
		expected:     "Ingress updated successfully",
		clientErrors: nilClientError,
	},
	{
		name:      "Ingress update fail",
		oldServer: inferenceEndpoint,
		newServer: crv1.InferenceEndpoint{
			TypeMeta:   metav1.TypeMeta{},
			ObjectMeta: metav1.ObjectMeta{},
			Spec:       crv1.InferenceEndpointSpec{EndpointName: "test", TemplateName: "test", SubjectName: "test"},
			Status:     crv1.InferenceEndpointStatus{}},
		expected:     "ERROR during ingress update operation",
		clientErrors: clientError{nil, nil, nil, nil, nil, errors.New("")},
	},
	{
		name:      "ModelName different",
		oldServer: inferenceEndpoint,
		newServer: crv1.InferenceEndpoint{
			TypeMeta:   metav1.TypeMeta{},
			ObjectMeta: metav1.ObjectMeta{},
			Spec:       crv1.InferenceEndpointSpec{EndpointName: "test", TemplateName: "test", ModelName: "test"},
			Status:     crv1.InferenceEndpointStatus{}},
		expected:     "Deployment updated successfully",
		clientErrors: nilClientError,
	},
	{
		name:      "Deployment update fail",
		oldServer: inferenceEndpoint,
		newServer: crv1.InferenceEndpoint{
			TypeMeta:   metav1.TypeMeta{},
			ObjectMeta: metav1.ObjectMeta{},
			Spec:       crv1.InferenceEndpointSpec{EndpointName: "test", TemplateName: "test", ModelName: "test"},
			Status:     crv1.InferenceEndpointStatus{}},
		expected:     "ERROR during deployment update operation",
		clientErrors: clientError{nil, nil, errors.New(""), nil, nil, nil},
	},
}

func testUpdate(oldServer, newServer crv1.InferenceEndpoint, errs clientError) string {
	var buf bytes.Buffer
	log.SetOutput(&buf)
	defer func() {
		log.SetOutput(os.Stderr)
	}()
	updateMap := createTemplateClients(errs)
	hooks := serverHooks{updateMap}
	oldInferenceEndpoint := oldServer
	newInferenceEndpoint := newServer
	hooks.Update(&oldInferenceEndpoint, &newInferenceEndpoint)
	return buf.String()
}

var inferenceEndpointsTestUpdateTemplate = []struct {
	name         string
	oldServer    crv1.InferenceEndpoint
	newServer    crv1.InferenceEndpoint
	expected     string
	clientErrors clientError
}{
	{
		name:         "No such template",
		oldServer:    inferenceEndpointEmpty,
		newServer:    inferenceEndpoint,
		expected:     "There is no such template",
		clientErrors: nilClientError,
	},
	{
		name:         "Success to update template",
		oldServer:    inferenceEndpoint,
		newServer:    inferenceEndpoint,
		expected:     "updated successfully",
		clientErrors: nilClientError,
	},
	{
		name:         "Config map update error",
		oldServer:    inferenceEndpoint,
		newServer:    inferenceEndpoint,
		expected:     "ERROR during configMap update",
		clientErrors: clientError{errors.New(""), nil, nil, nil, nil, nil}},
	{
		name:         "Deployment update error",
		oldServer:    inferenceEndpoint,
		newServer:    inferenceEndpoint,
		expected:     "ERROR during deployment update",
		clientErrors: clientError{nil, errors.New(""), nil, nil, nil, nil}},
	{
		name:         "Service deletion error",
		oldServer:    inferenceEndpoint,
		newServer:    inferenceEndpoint,
		expected:     "ERROR during service delete",
		clientErrors: clientError{nil, nil, nil, errors.New(""), nil, nil}},
	{
		name:         "Ingress update error",
		oldServer:    inferenceEndpoint,
		newServer:    inferenceEndpoint,
		expected:     "ERROR during ingress update",
		clientErrors: clientError{nil, nil, nil, nil, errors.New(""), nil}},
}

func testUpdateTemplate(oldServer, newServer crv1.InferenceEndpoint, errs clientError) string {
	var buf bytes.Buffer
	log.SetOutput(&buf)
	defer func() {
		log.SetOutput(os.Stderr)
	}()
	updateMap := createTemplateClients(errs)
	hooks := serverHooks{updateMap}
	oldInferenceEndpoint := oldServer
	newInferenceEndpoint := newServer
	hooks.updateTemplate(&oldInferenceEndpoint, &newInferenceEndpoint)
	return buf.String()
}

var patchDataTest = patchData{ModelName: "test", ModelVersionPolicy: "test", Namespace: "test", ResourcePath: "test"}

var dataTestPrepareJSONPatchFromMap = []struct {
	name          string
	resourceType  string
	mapPatch      []interface{}
	oldData       map[string]string
	newData       map[string]string
	patchData     patchData
	expectedError error
	resourcePath  string
}{
	{
		name:          "No changes",
		resourceType:  "test",
		mapPatch:      make([]interface{}, 0),
		oldData:       map[string]string{"test": "test"},
		newData:       map[string]string{"test": "test"},
		patchData:     patchDataTest,
		expectedError: nil,
		resourcePath:  "",
	},
	{
		name:          "Unequal maps",
		resourceType:  "test",
		mapPatch:      make([]interface{}, 0),
		oldData:       map[string]string{"test": "test"},
		newData:       map[string]string{"test1": "test"},
		patchData:     patchDataTest,
		expectedError: nil,
		resourcePath:  "",
	},
	{
		name:          "Wrong resource path",
		resourceType:  "test",
		mapPatch:      make([]interface{}, 0),
		oldData:       map[string]string{"test": "test"},
		newData:       map[string]string{"test1": "test"},
		patchData:     patchDataTest,
		expectedError: template.ExecError{Name: "New", Err: errors.New("can't evaluate field ResourcePathTest in type main.patchData")},
		resourcePath:  "{{.ResourcePathTest}}",
	},
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

func TestUpdate(t *testing.T) {
	for _, tt := range inferenceEndpointsTestUpdate {
		t.Run(tt.name, func(t *testing.T) {
			got := testUpdate(tt.oldServer, tt.newServer, tt.clientErrors)
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

func TestPrepareJSONPatchFromMap(t *testing.T) {
	for _, tt := range dataTestPrepareJSONPatchFromMap {
		t.Run(tt.name, func(t *testing.T) {
			if !(tt.resourcePath == "") {
				oldResourcePath := resourcePath
				defer func() {
					resourcePath = oldResourcePath
				}()
				resourcePath = tt.resourcePath
			}
			_, err := prepareJSONPatchFromMap(tt.resourceType, tt.mapPatch, tt.oldData, tt.newData, tt.patchData)
			if !(err == tt.expectedError) {
				if !strings.Contains(err.Error(), tt.expectedError.Error()) {
					t.Logf("Expected: (%s), got: (%s)\n", tt.expectedError, err)
					t.Fail()
				}
			}
		})
	}
}
