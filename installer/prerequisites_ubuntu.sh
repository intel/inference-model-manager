sudo apt-get install expect-dev -y
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
sudo apt-get install jq -y
wget https://github.com/mikefarah/yq/releases/download/2.2.1/yq_linux_amd64
chmod a+x yq_linux_amd64
sudo mv yq_linux_amd64 /usr/local/bin/yq
sudo add-apt-repository ppa:jonathonf/python-3.6
sudo apt-get update 
sudo apt-get install python3.6 -y
sudo apt-get install proxytunnel -y
sudo pip install --upgrade virtualenv
sudo pip install --upgrade pip
