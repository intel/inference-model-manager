#!/bin/bash
. ../utils/messages.sh
. ../utils/wait_for_pod.sh
header "Installing ingress controller"
cd $HELM_TEMP_DIR/ing-subchart
helm install .
header "Waiting for ingress controller pod"
wait_for_pod 60 nginx-ingress-controller ingress-nginx
cd -
