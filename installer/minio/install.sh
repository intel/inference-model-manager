. ../utils/fill_template.sh
. ../utils/messages.sh
MINIO_ACCESS_KEY=$1
MINIO_SECRET_KEY=$2
MINIO_EXTERNAL_URL=$3

header "Installing test minio storage"

cd ../../helm-deployment/minio-subchart
fill_template "<minio_access_key>" $MINIO_ACCESS_KEY  values.yaml
fill_template "<minio_secret_key>" $MINIO_SECRET_KEY values.yaml
helm install . -n test-minio
FAILED=$?
show_result "$FAILED" "Minio storage installed" "Failed to install Minio storage"
cd -
cp minio_ing_tmpl.yaml minio_ing.yaml
fill_template "<minio_external_url>" $MINIO_EXTERNAL_URL minio_ing.yaml
kubectl create -f minio_ing.yaml
FAILED=$?
show_result "$FAILED" "Minio ingress created at $MINIO_EXTERNAL_URL" "Failed to install Minio ingress"

