## Helm deployment of Inference Model Manager

#### Management API certificates
Management API uses certificates to serve API using TLS. 

If you prepared certificates, you have to place certs in `/helm-deployment/charts/management-api-subchart/certs`
Certificates should have names `man-api-server.crt` and `man-api-server.key`

If you want to you can use our script which generate necessary certificates.
Go to the directory mentioned earlier and run `management_api_certs.sh` and `internal_ing_man_api_certs.sh`.

### Platform deployment 

To get fully functional platform you have to install components:
- [CRD](crd-subchart/README.md)
- [INGRESS](ing-subchart/README.md)
- [DEX](dex-subchart/README.md)
- [MANAGEMENT-API](management-api-subchart/README.md)

If you dont have minio/s3 prepared you can use our deployment:
- [MINIO](minio-subchart/README.md)


##
### Certificate Revocation List

Commands to create empty CRL:

```
cd helm-deployment/certs
echo 01 > certserial
echo 01 > crlnumber
echo 01 > crlnumber
touch certindex
openssl ca -config ca.conf -gencrl -keyfile ca.key -cert ca.crt -out root.crl.pem
```
Command to revoke example client certificate:  
`openssl ca -config ca.conf -revoke client.crt -keyfile ca.key -cert ca.crt`
Add revoked certificate to CRL:  
`openssl ca -config ca.conf -gencrl -keyfile ca.key -cert ca.crt -out root.crl.pem`

Above command will update existing root.crl.pem file.

In order to add CRL support to ingress-nginx append content of root.crl.pem to ca-cert-tf.crt file

Remove old CRL appended to ca-cert-tf.crt if exists, and append new one with following command:  
`cat ca-cert-tf.crt root.crl.pem >> temporary`

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

**WARNING**: /inference-model-manager/helm-deployment/certs directory contains example ca.conf 
file required to create CRL list. Please adjust this configuration file to your environment before use in production.

##
### Dex connector configuration
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
