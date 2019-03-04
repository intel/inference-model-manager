## Deploy Kubernetes with Kubespray
## Example on Google Cloud Platform

Create VMs with gcloud:

```
gcloud compute instances create instance-1 instance-2 instance-3 --zone <zone> --can-ip-forward --tags=<network tags that manage firewall rules required for k8s cluster>
```

Clone kubespray repository.

Check IP adresses of above instances.

```
gcloud compute instances list --filter="name ~ instance-1" --format='value(EXTERNAL_IP)'
gcloud compute instances list --filter="name ~ instance-1" --format='value(INTERNAL_IP)'
```
Add following variables to inventory file (host.ini)
```
ansible_ssh_host=EXTERNAL_IP ansible_host=INTERNAL_IP access_ip=INTERNAL_IP ip=INTERNAL_IP
```
Note that your ssh key must be copied to all machines mentioned in inventory configuration.


Run ansible playbook inside clone of kubespray repository
```
ansible-playbook -u <user> -e ansible_ssh_user=admin -e cloud_provider=gce -b --become-user=root -i inventory/<your inventory configuration> cluster.yml --private-key=~/.ssh/private_key
```

Clone inference-model-manager repository and go through installation procedure.

### Enabling oidc authentication in Kubernetes installed via Kubespray

Changes required to enable oidc authentication in Kubernetes installed via Kubespray

```
cd /etc/kubernetes/manifests/
vi kube-apiserver.yaml
```
Add following flags with desired values

[More information about oidc flags here](../docs/deployment.md)

```
--oidc-issuer-url
--oidc-client-id
--oidc-groups-claim
--oidc-username-claim
--oidc-ca-file
```
After saving changes in kube-apiserver.yaml file, kubeapi server pod will be restarted automatically, what means that until pod is up & running again, kubectl commands will return connection refused errors.
```
kubectl get pods -n kube-system
The connection to the server <IP_ADDRESS>:6443 was refused - did you specify the right host or port?
```
If error occurs after few minutes, review updates in kube apiserver configuration and double check path to certificate file. Remember, to not to add `oidc-ca-file` flag before placing certificate file in right directory as kube apiserver pod will not start.

