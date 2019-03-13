
## CREATE CLUSTER MANUALLY
```
wget -O kops https://github.com/kubernetes/kops/releases/download/$(curl -s https://api.github.com/repos/kubernetes/kops/releases/latest | grep tag_name | cut -d '"' -f 4)/kops-linux-amd64

chmod +x ./kops
sudo mv ./kops /usr/local/bin/
export PROJECT=`gcloud config get-value project`
export KOPS_FEATURE_FLAGS=AlphaAllowGCE
export GOOGLE_APPLICATION_CREDENTIALS="/home/local/GER/username/.config/gcloud/legacy_credentials/user.name@intel.com/adc.json"

export CLUSTER_NAME="<clustername>"

sed -i "s/toreplacebyclustername/${CLUSTER_NAME}/g" desired.yaml
kops create -f desired.yaml
export KOPS_STATE_STORE=gs://kubernetes-clusters-imm
kops update cluster <clustername>.k8s.local --yes
export NAME=<cluster-name>.k8s.local
kops export kubecfg ${NAME}

kubectl create sa tiller --namespace kube-system
kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
helm init --debug --upgrade --service-account tiller

```
## ADD A RECORD IN AWS ROUTE 53

```
aws route53 change-resource-record-sets --hosted-zone-id Z11DOV0M5AJEBB --change-batch file://route_record.json
```
where route_record.json is a json file containing ingress ip (echo $ING_IP) and your domain name (example in /inferno-platform/installer/utils/route53 directory)


