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
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

	"github.com/intel/crd-reconciler-for-kubernetes/pkg/resource"
	"github.com/intel/crd-reconciler-for-kubernetes/pkg/states"
	"k8s.io/apimachinery/pkg/runtime"
)

type resourceError struct {
	createError error
	patchError  error
	updateError error
	deleteError error
}

type mockClient struct {
	errCreate error
	errPatch  error
	errUpdate error
	errDelete error
}

func newMockClient(err resourceError) resource.Client {
	return &mockClient{err.createError, err.patchError, err.updateError, err.deleteError}
}

func (*mockClient) Reify(templateValues interface{}) ([]byte, error) {
	return nil, nil
}

func (c *mockClient) Create(namespace string, templateValues interface{}) error {
	return c.errCreate
}

func (c *mockClient) Delete(namespace string, name string) error {
	return c.errDelete
}

func (c *mockClient) Update(namespace string, name string, templateValues interface{}) error {
	return c.errUpdate
}

func (c *mockClient) Patch(namespace string, name string, data []byte) error {
	return c.errPatch
}

func (*mockClient) Get(namespace, name string) (runtime.Object, error) {
	return nil, nil
}

func (*mockClient) List(namespace string, labels map[string]string) ([]metav1.Object, error) {
	return nil, nil
}

func (*mockClient) IsFailed(namespace string, name string) bool {
	return true
}

func (*mockClient) IsEphemeral() bool {
	return true
}

func (*mockClient) Plural() string {
	return ""
}

func (*mockClient) GetStatusState(runtime.Object) states.State {
	return states.Pending
}
