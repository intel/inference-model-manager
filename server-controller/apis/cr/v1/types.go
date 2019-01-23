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

package v1

import (
	"encoding/json"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/runtime/schema"

	"github.com/intel/crd-reconciler-for-kubernetes/pkg/states"
)

// GroupName is the group name used in this package.
const GroupName = "ai.intel.com"

// Version is the version used in this package
const Version = "v1"

// InferenceEndpointResourceKind is resource kind used in this package
const InferenceEndpointResourceKind = "InferenceEndpoint"

// InferenceEndpointResourceSingular is resource singular name used in this package
const InferenceEndpointResourceSingular = "inference-endpoint"

// InferenceEndpointResourcePlural is resource plural name used in this package
const InferenceEndpointResourcePlural = "inference-endpoints"

var (
	// GVK unambiguously identifies the stream prediction kind.
	GVK = schema.GroupVersionKind{
		Group:   GroupName,
		Version: Version,
		Kind:    InferenceEndpointResourceKind,
	}
)

// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object

// InferenceEndpoint represents state and metadata of Inference Endpoint
type InferenceEndpoint struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata"`
	Spec              InferenceEndpointSpec   `json:"spec"`
	Status            InferenceEndpointStatus `json:"status,omitempty"`
}

// Name return Inference Endpoint name
func (e *InferenceEndpoint) Name() string {
	return e.ObjectMeta.Name
}

// Namespace return Inference Endpoint namespace
func (e *InferenceEndpoint) Namespace() string {
	return e.ObjectMeta.Namespace
}

//JSON return Inference Endpoint metadata as JSON, error
func (e *InferenceEndpoint) JSON() (string, error) {
	data, err := json.Marshal(e)
	if err != nil {
		return "", err
	}

	return string(data), nil
}

// GetStatusState return Inference Endpoint status state
func (e *InferenceEndpoint) GetStatusState() states.State {
	return e.Status.State
}

// GetSpecState return Infernence Endpoint specification state
func (e *InferenceEndpoint) GetSpecState() states.State {
	return e.Spec.State
}

//SetStatusStateWithMessage allows to overwrite Inference Endpoint state and message
func (e *InferenceEndpoint) SetStatusStateWithMessage(state states.State, msg string) {
	e.Status.State = state
	e.Status.Message = msg
}

// InferenceEndpointSpec represents all metadata included in Inference Endpoint
type InferenceEndpointSpec struct {
	State              states.State `json:"state"`
	ModelName          string       `json:"modelName"`
	ModelVersionPolicy string       `json:"modelVersionPolicy"`
	EndpointName       string       `json:"endpointName,omitempty"`
	SubjectName        string       `json:"subjectName"`
	Resources          ResourceSpec `json:"resources,omitempty"`
	Replicas           int          `json:"replicas,omitempty"`
	TemplateName       string       `json:"servingName"`
}

// InferenceEndpointStatus stores information about state and message in Inference Endpoint
type InferenceEndpointStatus struct {
	State   states.State `json:"state"`
	Message string       `json:"message,omitempty"`
}

// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object

// InferenceEndpointList represents list of Inference Endpoints
type InferenceEndpointList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata"`
	Items           []InferenceEndpoint `json:"items"`
}

// ResourceSpec represents resource requests and limits used in Inference Endpoint
type ResourceSpec struct {
	Requests map[string]string `json:"requests"`
	Limits   map[string]string `json:"limits"`
}

// GetItems returns the list of items to be used in the List api call for crs
func (el *InferenceEndpointList) GetItems() []runtime.Object {
	var result []runtime.Object
	for _, item := range el.Items {
		ecCopy := item
		result = append(result, &ecCopy)
	}
	return result
}
