## Kubernetes deployment using Kops

#### Install Kops
```
wget -O kops https://github.com/kubernetes/kops/releases/download/$(curl -s https://api.github.com/repos/kubernetes/kops/releases/latest | grep tag_name | cut -d '"' -f 4)/kops-linux-amd64
chmod +x ./kops
sudo mv ./kops /usr/local/bin/
```

#### Create bucket to store k8s cluster configuration
```
gsutil mb gs://kubernetes-clusters-inferno/
```

#### Create all required environment variables
```
export PROJECT=`gcloud config get-value project`
export KOPS_FEATURE_FLAGS=AlphaAllowGCE
export GOOGLE_APPLICATION_CREDENTIALS="/home/<user.name>/.config/gcloud/legacy_credentials/<user.name>@email.com/adc.json"
```
Replace bucket name if needed
```
export KOPS_STATE_STORE=gs://kubernetes-clusters-inferno
```

#### Create cluster
```
kops create cluster <cluster-name>.k8s.local --zones us-central1-a --state gs://kubernetes-clusters-inferno --project=${PROJECT}
kops update cluster <cluster-name>.k8s.local --yes
export NAME=<cluster-name>.k8s.local
kops export kubecfg ${NAME}
```

#### Validate deployment
```
kubectl get nodes --show-labels
```

#### Delete deployment
```
kops delete cluster <cluster-name> --yes
```
