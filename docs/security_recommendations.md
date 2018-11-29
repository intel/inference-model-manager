# Security recommendations

Beside the mandatory [requirements and prerequisites](prerequisites.md) there are a few recommendations
for Kubernetes setup to ensure secure and reliable experience in the production usage.

- consider using an overlay network that implements network policy
- keeping the kubernetes master nodes separate from worker nodes
- enabling encryption on etcd to protect secrets
- ensuring the unauthenticated api server ports are blocked
- consider host-level inbound firewall policy
- audit your K8S cluster using [CIS Security benchmark](https://www.cisecurity.org/benchmark/kubernetes/)