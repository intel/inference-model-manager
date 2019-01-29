# Serving templates

Templates allow you to prepare optimized serving configurations which can be consumed by the platform users. 
Their goal is to simplify the process of management of inference services and maximizing the system performance.
Users can use only the templates enabled by the cluster administrators. It ensures best users experience and avoids
potential challenges with Kubernetes configuration. 

The administrator can enable the predefined templates, which are optimized for deployments of TensorFlow Serving* and OpenVINO
Model Server*. They can be changed and added with various settings like
environment variables, docker images, resource assignments etc. 


## Create custom template
The predefined templates are stored in [serving-templates folder](../helm-deployment/crd-subchart/serving-templates).
Each template is represented by a folder with 4 mandatory files:
 - deployment.tmpl
 - service.tmpl
 - ingress.tmpl
 - configMap.tmpl

Below are exemplary files including description of their elements. You can modify them, but preserve and complete the required fields.
They must also follow Kubernetes records definition.
It is generally a good habit to leave all places where `{{.}}` appears, because it means that it is filled by the CRD.
All ``<..>`` should be replaced.

```yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:  # All metadata variables and values specify below are necessary to properly work server-controller
  name: "{{.Spec.EndpointName}}"
  namespace: "{{.ObjectMeta.Namespace}}"
  labels:
    id: "{{.Spec.EndpointName}}"
    endpoint: "{{.Spec.EndpointName}}"
  ownerReferences: # Do not remove it. It is needed by server-controller for a cleanup after Endpoints are removed. 
  - apiVersion: {{.APIVersion}}
    kind: {{.Kind}}
    name: {{.Name}}
    uid: {{.UID}}
    controller: {{.Controller}}
    blockOwnerDeletion: {{.BlockOwnerDeletion}}
spec:
  replicas: {{or .Spec.Replicas 1}} # If you want the user to be able to specify the number of replicas 
                                    # leave this parameter, in another case enforce how many 
                                    # replicas are required
  minReadySeconds: 60
  template: #Required due to update operation
    metadata:
      labels:
        endpoint: "{{.Spec.EndpointName}}"
    spec:
      volumes: # If your template don't need any config maps mounted in the serving pods - you can remove this section
      - name: configmap
        configMap:
            name: "{{.Spec.EndpointName}}" # All resources created with Inference Endpoint have the same name
      containers:
      - name: <name>
        image: <Path to Image>
        imagePullPolicy: IfNotPresent
        command:
        - /bin/sh
        - -c
        args:
        - <>
        ports:
        - containerPort: <exposed port>
        volumeMounts: # You can remove this section if configmap don't need to be mounted in the serving pods
        - mountPath: /config/
          name: configmap
        env:
          <Environment Variables>
        resources: # If you want the user to be able to specify resources limits and requests leave this 
                   # section, otherwise specify on your own or remove this section completely if you dont 
                   # want specify any resources
          limits: 
{{ range $resource, $request := .Spec.Resources.Limits }}
            {{ $resource }}: "{{ $request }}"
{{ end }}
          requests:
{{ range $resource, $request := .Spec.Resources.Requests }}
            {{ $resource }}: "{{ $request }}"
{{ end }}
```

### ConfigMap

Even if you don`t want to use config maps in your template, you have to prepare one.

```yaml
# In this file only thing you can change is "data" section, but fill free to add some other metadata values.
apiVersion: v1
kind: ConfigMap
metadata:
  name: "{{.Spec.EndpointName}}"
  namespace: "{{.ObjectMeta.Namespace}}"
  labels:
    id: "{{.Spec.EndpointName}}"
    endpoint: "{{.Spec.EndpointName}}"
  ownerReferences: # Values needed for server-controller to delete all resources belongs to InferenceEndpoint
  - apiVersion: {{.APIVersion}}
    kind: {{.Kind}}
    name: {{.Name}}
    uid: {{.UID}}
    controller: {{.Controller}}
    blockOwnerDeletion: {{.BlockOwnerDeletion}}
data:
```

### Service

```yaml
# All variables below are required for proper work server controller
apiVersion: v1
kind: Service
metadata:
  name: "{{.Spec.EndpointName}}"
  namespace: "{{.ObjectMeta.Namespace}}"
  labels:
    id: "{{.Spec.EndpointName}}"
    endpoint: "{{.Spec.EndpointName}}"
  ownerReferences: # Values needed for server-controller to delete all resources belongs to InferenceEndpoint
  - apiVersion: {{.APIVersion}}
    kind: {{.Kind}}
    name: {{.Name}}
    uid: {{.UID}}
    controller: {{.Controller}}
    blockOwnerDeletion: {{.BlockOwnerDeletion}}
spec:
  selector:
    endpoint: "{{.Spec.EndpointName}}" # Must match to label created in deployment
  ports: # Must match with ports exposed in deployment 
  - port: <port>
    targetPort: <port>
```

### Ingress

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: "{{.Spec.EndpointName}}"
  namespace: "{{.ObjectMeta.Namespace}}"
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/grpc-backend: "true"
    nginx.ingress.kubernetes.io/auth-tls-verify-client: "on"
    nginx.ingress.kubernetes.io/auth-tls-secret: "{{.ObjectMeta.Namespace}}/ca-cert-secret"
    nginx.ingress.kubernetes.io/auth-tls-verify-depth: "1"
    nginx.ingress.kubernetes.io/auth-tls-pass-certificate-to-upstream: "false"
    nginx.ingress.kubernetes.io/proxy-body-size: 8m
    allowed-values: "CN={{.Spec.SubjectName}}"
  labels:
    id: "{{.Spec.EndpointName}}"
    endpoint: "{{.Spec.EndpointName}}"
  ownerReferences: # Values needed for server-controller to delete all resources belongs to InferenceEndpoint
  - apiVersion: {{.APIVersion}}
    kind: {{.Kind}}
    name: {{.Name}}
    uid: {{.UID}}
    controller: {{.Controller}}
    blockOwnerDeletion: {{.BlockOwnerDeletion}}
spec:
  rules:
  - host: {{.Spec.EndpointName}}-{{.ObjectMeta.Namespace}}.{{ GlobalTemplateValue "platformDomain" }}
    http:
      paths:
      - backend:
          serviceName: "{{.Spec.EndpointName}}"
          servicePort: <port> # Must match with port exposed in service
  tls:
  - hosts:
    - {{.Spec.EndpointName}}-{{.ObjectMeta.Namespace}}.{{ GlobalTemplateValue "platformDomain" }}
    secretName: tls-secret # Secret with TLS managed by Management-Api
```
                 
### Deployment

After configuring the templates in [serving-templates](../helm-deployment/crd-subchart/serving-templates) directory
you can apply them to the platform by upgrading the helm deployment of the crd-subchart.

Make sure you are using correct parameters in values.yaml to avoid misconfiguration of existing deployment.

```bash
helm upgrade `helm list --deployed | grep crd-subchart | cut -d" " -f1`  .
```                                      
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         