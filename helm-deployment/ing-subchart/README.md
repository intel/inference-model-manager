## Helm deployment of Ingress

### Preparation to installation

Before installation you have to make sure if all required certifications and keys are stored in ``/certs`` directory.
List of required files:
```
server-tf.crt
server-tf.key
ca-cert-tf.crt
```

If you don`t have prepared certs, you can use our scripts in ``/certs`` directory, which create all required files.
Warning!!!
Certifications make by this scripts are self-signed.

### Installation

To install this chart after preparation phase use:
```helm install .```