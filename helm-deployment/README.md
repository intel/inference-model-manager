# HELM DEPLOYMENT OF INFERENCE PLATFORM

```
cd helm-deployment
helm dep up .
helm install .
```
`helm dep up .` will download minio and dex as subcharts
`helm install .` will deploy all components on exisitng kubernetes cluster

It is possible to override subchart's values.yaml variables by adding 
```
subchart:
  variable: Something
```
in parent chart.

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

In order to add CRL support to ingress-nginx append content of root.crl.pem to ca-cert-secret.crt file

`cat root.crl.pem ca-cert-secret.crt >> ca-cert-secret.crt`

WARNING: /inferno-platform/helm-deployment/certs directory contains example ca.conf file required to create CRL list. Please adjust this configuration file to your environment before use in production.
