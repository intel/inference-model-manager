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
