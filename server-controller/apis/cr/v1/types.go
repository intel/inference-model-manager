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

package v1

import (
	"encoding/json"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/apimachinery/pkg/runtime"

	"github.com/NervanaSystems/kube-controllers-go/pkg/states"
)

// GroupName is the group name used in this package.
const GroupName = "intel.com"

const Version = "v1"

const ServerResourceKind = "Server"

const ServerResourceSingular = "server"

const ServerResourcePlural = "servers"

var (
	// GVK unambiguously identifies the stream predicition kind.
	GVK = schema.GroupVersionKind{
		Group:   GroupName,
		Version: Version,
		Kind:    ServerResourceKind,
	}
)

// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object
type Server struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata"`
	Spec              ServerSpec   `json:"spec"`
	Status            ServerStatus `json:"status,omitempty"`
}

func (e *Server) Name() string {
	return e.ObjectMeta.Name
}

func (e *Server) Namespace() string {
	return e.ObjectMeta.Namespace
}

func (e *Server) JSON() (string, error) {
	data, err := json.Marshal(e)
	if err != nil {
		return "", err
	}

	return string(data), nil
}

func (e *Server) GetStatusState() states.State {
	return e.Status.State
}

func (e *Server) GetSpecState() states.State {
	return e.Spec.State
}

func (e *Server) SetStatusStateWithMessage(state states.State, msg string) {
	e.Status.State = state
	e.Status.Message = msg
}

type ServerSpec struct {
	State           states.State             `json:"state"`
	ModelName       string                   `json:"modelName"`
	ModelVersion    int                      `json:"modelVersion"`
	EndpointName    string                   `json:"endpointName,omitempty"`
	SubjectName     string                   `json:"subjectName"`
	Resources       ResourceSpec             `json:"resources,omitempty"`
	Replicas        int                      `json:"replicas,omitempty"`
}

type ServerStatus struct {
	State   states.State `json:"state"`
	Message string       `json:"message,omitempty"`
}

// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object
type ServerList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata"`
	Items           []Server `json:"items"`
}

type ResourceSpec struct {
	Requests map[string]string `json:"requests"`
	Limits map[string]string `json:"limits"`
}

// GetItems returns the list of items to be used in the List api call for crs
func (el *ServerList) GetItems() []runtime.Object {
	var result []runtime.Object
	for _, item := range el.Items {
		ecCopy := item
		result = append(result, &ecCopy)
	}
	return result
}
