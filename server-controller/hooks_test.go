package main

import (
	"bytes"
	"errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"log"
	"testing"

	"github.com/intel/crd-reconciler-for-kubernetes/pkg/resource"
	"github.com/intel/crd-reconciler-for-kubernetes/pkg/states"

	crv1 "github.com/IntelAI/inference-model-manager/server-controller/apis/cr/v1"
	"os"
	"strings"
)

type mockClient struct {
	err error
}

func NewMockClient(err error) resource.Client {
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

type clientErr struct {
	configMapError        error
	deploymentClientError error
	serviceClientError    error
	ingressClientError    error
}

var inferenceEndpointsTest = []struct {
	name              string
	inferenceEndpoint crv1.InferenceEndpoint
	expected          string
	clientErrors      clientErr
}{
	{
		name: "No template provided",
		inferenceEndpoint: crv1.InferenceEndpoint{
			TypeMeta:   metav1.TypeMeta{},
			ObjectMeta: metav1.ObjectMeta{},
			Spec:       crv1.InferenceEndpointSpec{},
			Status:     crv1.InferenceEndpointStatus{},
		},
		expected:     "There is no such template",
		clientErrors: clientErr{nil, nil, nil, nil}},
	{
		name: "Success to create template",
		inferenceEndpoint: crv1.InferenceEndpoint{
			TypeMeta:   metav1.TypeMeta{},
			ObjectMeta: metav1.ObjectMeta{},
			Spec:       crv1.InferenceEndpointSpec{EndpointName: "test", TemplateName: "test"},
			Status:     crv1.InferenceEndpointStatus{}},
		expected:     "created successfully",
		clientErrors: clientErr{nil, nil, nil, nil}},
	{
		name: "Config map creation error",
		inferenceEndpoint: crv1.InferenceEndpoint{
			TypeMeta:   metav1.TypeMeta{},
			ObjectMeta: metav1.ObjectMeta{},
			Spec:       crv1.InferenceEndpointSpec{EndpointName: "test", TemplateName: "test"},
			Status:     crv1.InferenceEndpointStatus{}},
		expected:     "ERROR during configMap creation",
		clientErrors: clientErr{errors.New(""), nil, nil, nil}},
	{
		name: "Deployment creation error",
		inferenceEndpoint: crv1.InferenceEndpoint{
			TypeMeta:   metav1.TypeMeta{},
			ObjectMeta: metav1.ObjectMeta{},
			Spec:       crv1.InferenceEndpointSpec{EndpointName: "test", TemplateName: "test"},
			Status:     crv1.InferenceEndpointStatus{}},
		expected:     "ERROR during deployment creation",
		clientErrors: clientErr{nil, errors.New(""), nil, nil}},
	{
		name: "Service creation error",
		inferenceEndpoint: crv1.InferenceEndpoint{
			TypeMeta:   metav1.TypeMeta{},
			ObjectMeta: metav1.ObjectMeta{},
			Spec:       crv1.InferenceEndpointSpec{EndpointName: "test", TemplateName: "test"},
			Status:     crv1.InferenceEndpointStatus{}},
		expected:     "ERROR during service creation",
		clientErrors: clientErr{nil, nil, errors.New(""), nil}},
	{
		name: "Ingress creation error",
		inferenceEndpoint: crv1.InferenceEndpoint{
			TypeMeta:   metav1.TypeMeta{},
			ObjectMeta: metav1.ObjectMeta{},
			Spec:       crv1.InferenceEndpointSpec{EndpointName: "test", TemplateName: "test"},
			Status:     crv1.InferenceEndpointStatus{}},
		expected:     "ERROR during ingress creation",
		clientErrors: clientErr{nil, nil, nil, errors.New("")}},
}

func serverAdd(infer crv1.InferenceEndpoint, errs clientErr) string {
	var buf bytes.Buffer
	log.SetOutput(&buf)
	defer func() {
		log.SetOutput(os.Stderr)
	}()

	updateMap := make(map[string]templateClients)
	configMapClient := NewMockClient(errs.configMapError)
	deploymentClient := NewMockClient(errs.deploymentClientError)
	serviceClient := NewMockClient(errs.serviceClientError)
	ingressClient := NewMockClient(errs.ingressClientError)
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
			got := serverAdd(tt.inferenceEndpoint, tt.clientErrors)
			if !strings.Contains(got, tt.expected) {
				t.Logf("Expected: (%s), got: (%s)\n", tt.expected, got)
				t.Fail()
			}
		})
	}
}
