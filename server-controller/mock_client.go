package main

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

	"github.com/intel/crd-reconciler-for-kubernetes/pkg/resource"
	"github.com/intel/crd-reconciler-for-kubernetes/pkg/states"
	"k8s.io/apimachinery/pkg/runtime"
)

type mockClient struct {
	err error
}

func newMockClient(err error) resource.Client {
	return &mockClient{err}
}

func (*mockClient) Reify(templateValues interface{}) ([]byte, error) {
	return nil, nil
}

func (c *mockClient) Create(namespace string, templateValues interface{}) error {
	return c.err
}

func (*mockClient) Delete(namespace string, name string) error {
	return nil
}

func (*mockClient) Update(namespace string, name string, templateValues interface{}) error {
	return nil
}

func (*mockClient) Patch(namespace string, name string, data []byte) error {
	return nil
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
