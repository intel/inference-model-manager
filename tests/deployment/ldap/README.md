## IMM Test ldap

In this directory are stored files directly needed to launch Openldap helm chart used by our functional and e2e tests.

### Installation

```helm install --name <release name> -f values.yaml stable/openldap```