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
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/apimachinery/pkg/runtime"

	"github.com/intel/crd-reconciler-for-kubernetes/pkg/states"
)

// GroupName is the group name used in this package.
const GroupName = "ai.intel.com"

const Version = "v1"

const InferenceEndpointResourceKind = "InferenceEndpoint"

const InferenceEndpointResourceSingular = "inference-endpoint"

const InferenceEndpointResourcePlural = "inference-endpoints"

var (
	// GVK unambiguously identifies the stream predicition kind.
	GVK = schema.GroupVersionKind{
		Group:   GroupName,
		Version: Version,
		Kind:    InferenceEndpointResourceKind,
	}
)

// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object
type InferenceEndpoint struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata"`
	Spec              InferenceEndpointSpec   `json:"spec"`
	Status            InferenceEndpointStatus `json:"status,omitempty"`
}

func (e *InferenceEndpoint) Name() string {
	return e.ObjectMeta.Name
}

func (e *InferenceEndpoint) Namespace() string {
	return e.ObjectMeta.Namespace
}

func (e *InferenceEndpoint) JSON() (string, error) {
	data, err := json.Marshal(e)
	if err != nil {
		return "", err
	}

	return string(data), nil
}

func (e *InferenceEndpoint) GetStatusState() states.State {
	return e.Status.State
}

func (e *InferenceEndpoint) GetSpecState() states.State {
	return e.Spec.State
}

func (e *InferenceEndpoint) SetStatusStateWithMessage(state states.State, msg string) {
	e.Status.State = state
	e.Status.Message = msg
}

type InferenceEndpointSpec struct {
	State           states.State             `json:"state"`
	ModelName       string                   `json:"modelName"`
	ModelVersion    int                      `json:"modelVersion"`
	EndpointName    string                   `json:"endpointName,omitempty"`
	SubjectName     string                   `json:"subjectName"`
	Resources       ResourceSpec             `json:"resources,omitempty"`
	Replicas        int                      `json:"replicas,omitempty"`
	TemplateName    string                   `json:"servingName"`
}

type InferenceEndpointStatus struct {
	State   states.State `json:"state"`
	Message string       `json:"message,omitempty"`
}

// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object
type InferenceEndpointList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata"`
	Items           []InferenceEndpoint `json:"items"`
}

type ResourceSpec struct {
	Requests map[string]string `json:"requests"`
	Limits map[string]string `json:"limits"`
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
