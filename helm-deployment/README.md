# HELM DEPLOYMENT OF INFERENCE PLATFORM

```
cd helm-deployment
helm dep up .
helm install --name inferno-platform . 
```
`helm dep up .` will download minio and dex as subcharts
`helm install --name inferno-platform .` will deploy all components on exisitng kubernetes cluster. Release will be named 'inferno-platform'.

In case of problems with tiller make sure that service account tiller is created:
```
kubectl create sa tiller --namespace kube-system
kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
helm init --debug --upgrade --service-account tiller
```

It is possible to override subchart's values.yaml variables by adding 
```
subchart:
  variable: Something
```
in parent chart.
WARNING: Values for dex have to be passed to helm config. They are passed using separate yaml file, but if you prefer you can put your values using method given above.
WARNING: There are test keys and certificates included in this helm deployment (/inferno-platform/helm-deployment/certs), please replace them with secure certificates in case of production deployment.

In order to overwrite minio credentials edit values.yaml file. 
Please do not provide minio credentials as argument in `helm install .` command

# Certificate Revocation List

Commands to create empty CRL:

```
cd helm-deployment/certs
echo 01 > certserial
echo 01 > crlnumber
echo 01 > crlnumber
touch certindex
openssl ca -config ca.conf -gencrl -keyfile ca.key -cert ca.crt -out root.crl.pem

```
Command to revoke example client certificate
`openssl ca -config ca.conf -revoke client.crt -keyfile ca.key -cert ca.crt`
Add revoked certificate to CRL
`openssl ca -config ca.conf -gencrl -keyfile ca.key -cert ca.crt -out root.crl.pem`

Above command will update existing root.crl.pem file.

In order to add CRL support to ingress-nginx append content of root.crl.pem to ca-cert-secret.crt file

Remove old CRL appended to ca-cert-secret.crt if exists, and append new one with following command:

`cat ca-cert-secret.crt root.crl.pem >> temporary`

Encode with base64 `cat temporary | base64 -w0`
and copy paste to kubernetes secret `kubectl edit secret ca-cert-secret` in place of ca.crt.
Delete old controller pod:

```
kubectl get pods -n ingress-nginx
kubectl delete pod nginx-ingress-controller-6b4ccdc495-wkfq4 -n ingress-nginx
```

Above commands should result with 400 response for client which is configured to use client.crt

```  
File "client.py", line 51, in <module>
    result = stub.Predict(request, 10.0)  # 10 secs timeout
  File "/usr/local/lib/python2.7/dist-packages/grpc/beta/_client_adaptations.py", line 309, in __call__
    self._request_serializer, self._response_deserializer)
  File "/usr/local/lib/python2.7/dist-packages/grpc/beta/_client_adaptations.py", line 195, in _blocking_unary_unary
    raise _abortion_error(rpc_error_call)
grpc.framework.interfaces.face.face.CancellationError: CancellationError(code=StatusCode.CANCELLED, details="Received http2 header with status: 400")
```

WARNING: /inferno-platform/helm-deployment/certs directory contains example ca.conf file required to create CRL list. Please adjust this configuration file to your environment before use in production.

# Dex connector configuration
In `helm-deployment/dex-subchart/values.yaml` there is a section about connector (`config
.connectors`). If you would like to use a different one - please provide additional dex-values.yaml
with proper configuration, which would override ldap connector.
Example:
```
dex:
  config:
    connectors:
    - type: <connector type, i.e. ldap>
      name: <connector name, i.e. OpenLDAP>
      id: <id, i.e. ldap>
      config:
        <new connector configuration>
```
