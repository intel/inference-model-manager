. ../utils/fill_template.sh

cd ../../server-controller

REGISTRY_URL=$1
export IMAGE=$2
export TAG=$3
DOMAIN_NAME=$4
make docker_build
NAME_WITH_REG=${REGISTRY_URL}${IMAGE}
WHOLE_TAG=${NAME_WITH_REG}:${TAG}
docker tag $IMAGE:$TAG ${REGISTRY_URL}${IMAGE}:${TAG}
docker push $WHOLE_TAG
cd -

cd ../../helm-deployment/crd-subchart

fill_template "<crd_image_path>" $NAME_WITH_REG values.yaml
fill_template "<crd_image_tag>" $TAG values.yaml
fill_template "<dns_domain_name>" $DOMAIN_NAME values.yaml
helm install .
cd -
pwd
