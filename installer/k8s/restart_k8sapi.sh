. ../utils/fill_template.sh
. ../utils/messages.sh
export PROJECT=`gcloud config get-value project`
export KOPS_FEATURE_FLAGS=AlphaAllowGCE
export GOOGLE_APPLICATION_CREDENTIALS="/Users/kbalka/.config/gcloud/legacy_credentials/krzysztof.balka@intel.com/adc.json"
export KOPS_STATE_STORE=gs://kubernetes-clusters-imm
```

#### Update cluster

```
CLUSTER_NAME=$1
ISSUER=$2
DEX_NAMESPACE=$3

header "Restarting k8s api with params: cluster name: $CLUSTER_NAME issuer: $ISSUER dex namespace: $DEX_NAMESPACE"

cp oidc_tmpl.yaml oidc.yaml

fill_template toreplacebyissuer $ISSUER oidc.yaml

DEX_ING_CA=`kubectl get secret ca-ing-dex -n $DEX_NAMESPACE -o yaml|grep ca.crt|awk '{ print $2 }'|base64 --decode > ca-ing-dex.crt`
${SED_CMD} -i -e 's/^/      /' ca-ing-dex.crt 
${SED_CMD} -i -e '/replacebycertificate/{r ca-ing-dex.crt' -e 'd}' oidc.yaml
OIDC_CFG=`cat oidc.yaml`

kops get cluster --name $CLUSTER_NAME.k8s.local --output json > config.yaml
yq m config.yaml oidc.yaml > config_oidc.yaml
cat config_oidc.yaml
kops replace -f config_oidc.yaml 
header "Configuration updated, restarting cluster"
kops update cluster --yes 
kops rolling-update cluster --yes
show_result $? "Restart succeded" "Restart failed"

