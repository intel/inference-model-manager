## Deploy Kubernetes with Kubespray
## Example on Google Cloud Platform

Create VMs with gcloud:
```
gcloud compute instances create instance-1 instance-2 instance-3 --zone <zone>
```
Clone kubespray repository.
Check IP adresses of above instances and add them to inventory definition of your cluster.
Note that your ssh key must be copied to all machines mentioned in inventory configuration.

Run ansible playbook inside clone of kubespray repository
ansible-playbook -u <user> -e ansible_ssh_user=admin -e cloud_provider=gce -b --become-user=root -i inventory/<your inventory configuration> cluster.yml --private-key=~/.ssh/private_key


Clone inference-model-manager repository and go through installation procedure.

### Enabling oidc authentication in Kubernetes installed via Kubespray

Changes required to enable oidc authentication in Kubernetes installed via Kubespray

```
cd /etc/kubernetes/manifests/
vi kube-apiserver.yaml
```
Add following flags with desired values
[More information about oidc flags here](../blob/master/docs/deployment.md)

```
--oidc-issuer-url
--oidc-client-id
--oidc-groups-claim
--oidc-username-claim
--oidc-ca-file # path to file
```
After saving changes in kube-apiserver.yaml file, kubeapi server pod will be restarted automatically, what means that until pod is up & running again, kubectl commands will return connection refused errors.
```
kubectl get pods -n kube-system
The connection to the server <IP_ADDRESS>:6443 was refused - did you specify the right host or port?
```
If error occurs after few minutes, review updates in kube apiserver configuration and double check path to certificate file. Remember, to not to add `oidc-ca-file` flag before placing certificate file in right directory as kube apiserver pod will not start.

