#!/bin/bash
. ../utils/wait_for_pod.sh
. ../utils/progress_bar.sh
. ../utils/messages.sh

header "Installing tiller on k8s"

kubectl -n kube-system create serviceaccount tiller

kubectl create clusterrolebinding tiller \
  --clusterrole cluster-admin \
  --serviceaccount=kube-system:tiller

helm init --service-account tiller
show_result $? "Tiller installed" "Failed to install tiller"
echo "Waiting for tiller pod to be ready"
wait_for_pod 60 tiller-deploy kube-system
# extra wait because presence of tiller is not enough
echo "Extra wait for 10s"
progress_bar 10


