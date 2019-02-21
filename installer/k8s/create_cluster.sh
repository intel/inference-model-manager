#!/bin/bash
. ../utils/progress_bar.sh
. ../utils/fill_template.sh
. ../utils/messages.sh

export PROJECT=`gcloud config get-value project`
export KOPS_FEATURE_FLAGS=AlphaAllowGCE
if [ ! -z "$GCE_USER" ]; then
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/gcloud/legacy_credentials/$GCE_USER/adc.json"
fi
export KOPS_STATE_STORE=gs://kubernetes-clusters-imm
```
#### Create cluster
```

header "Installing kubernetes cluster"

CLUSTER_NAME=$1
GCE_REGION=$2
cp cluster_template.yaml cluster.yaml
fill_template toreplacebyclustername $CLUSTER_NAME cluster.yaml
fill_template us-west1 ${GCE_REGION} cluster.yaml
kops create -f cluster.yaml
kops update cluster $CLUSTER_NAME.k8s.local --yes
show_result $? "Kubernetes cluster created" "Failed to create cluster" 
echo "Waiting 300 seconds for cluster to be ready"
progress_bar 300
header "Installing weave"
kubectl create -f https://git.io/weave-kube-1.6
show_result $? "Weave installed" "Failed to install weave"