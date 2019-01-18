. ../utils/messages.sh
. ../utils/wait_for_pod.sh
header "Installing ingress controller"
cd ../../helm-deployment/ing-subchart
helm install .
header "Waiting for ingress controller pod"
wait_for_pod 60 nginx-ingress-controller ingress-nginx
cd -
