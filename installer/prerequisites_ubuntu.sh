sudo apt-get install expect expect-dev -y
sudo apt-get install -y software-properties-common
KOPS=`command -v kops`
if [ -z "$KOPS" ]; then
curl -LO https://github.com/kubernetes/kops/releases/download/$(curl -s https://api.github.com/repos/kubernetes/kops/releases/latest | grep tag_name | cut -d '"' -f 4)/kops-linux-amd64
chmod +x kops-linux-amd64
sudo mv kops-linux-amd64 /usr/local/bin/kops
fi

HELM=`command -v helm`
if [ -z "$HELM" ]; then
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get > get_helm.sh
chmod 700 get_helm.sh
./get_helm.sh
helm init
fi

KUBECTL=`command -v kubectl`
if [ -z "$KUBECTL" ]; then
sudo apt-get update && sudo apt-get install -y apt-transport-https
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl
fi

sudo apt-get install jq -y
YQ=`command -v yq`
if [ -z "$YQ" ]; then
wget https://github.com/mikefarah/yq/releases/download/2.2.1/yq_linux_amd64
chmod a+x yq_linux_amd64
sudo mv yq_linux_amd64 /usr/local/bin/yq
fi
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.6 -y
sudo apt-get install proxytunnel -y
sudo apt-get install python-pip -y
sudo apt-get install python3-pip -y
sudo pip3 install --upgrade virtualenv 
sudo pip3 install --upgrade pip 
