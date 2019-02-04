package main

import (
	"bytes"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"log"
	"testing"

	"github.com/intel/crd-reconciler-for-kubernetes/pkg/resource"
	"github.com/intel/crd-reconciler-for-kubernetes/pkg/states"

	crv1 "github.com/IntelAI/inference-model-manager/server-controller/apis/cr/v1"
	"os"
	"strings"
	"k8s.io/client-go/rest"
)

type mockClient struct {
	mockRestClient rest.Interface
}

func NewMockClient() resource.Client {
	return &mockClient{}
}

func (*mockClient) Reify(templateValues interface{}) ([]byte, error) {
	return nil, nil
}

func (*mockClient) Create(namespace string, templateValues interface{}) error {
	return nil
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

var inferenceEndpointsTest = []struct {
	name              string
	inferenceEndpoint crv1.InferenceEndpoint
	expected          string
}{
	{"No template provided", crv1.InferenceEndpoint{metav1.TypeMeta{}, metav1.ObjectMeta{}, crv1.InferenceEndpointSpec{}, crv1.InferenceEndpointStatus{}}, "There is no such template"},
	{"Success to create template", crv1.InferenceEndpoint{metav1.TypeMeta{}, metav1.ObjectMeta{}, crv1.InferenceEndpointSpec{EndpointName: "test", TemplateName: "test"}, crv1.InferenceEndpointStatus{}}, "ERROR"},
}

func serverAdd(infer crv1.InferenceEndpoint) string {
	var buf bytes.Buffer
	log.SetOutput(&buf)
	defer func() {
		log.SetOutput(os.Stderr)
	}()

	updateMap := make(map[string]templateClients)
	deploymentClient := NewMockClient()
	serviceClient := NewMockClient()
	ingressClient := NewMockClient()
	configMapClient := NewMockClient()
	k8sClients := templateClients{deploymentClient, serviceClient, ingressClient, configMapClient}
	updateMap["test"] = k8sClients
	hooks := serverHooks{updateMap}
	inferenceEndpoint := infer
	hooks.Add(&inferenceEndpoint)
	return buf.String()
}

func TestAdd(t *testing.T) {
	for _, tt := range inferenceEndpointsTest {
		t.Run(tt.name, func(t *testing.T) {
			got := serverAdd(tt.inferenceEndpoint)
			if strings.Contains(tt.expected, got) {
				t.Logf("Expected: (%s), got: (%s)\n", tt.expected, got)
				t.Fail()
			}
		})
	}
}
