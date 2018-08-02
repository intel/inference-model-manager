IMAGE ?= 'management-api'
TAG ?= 'latest'

MANAGEMENT_HOSTNAME := "0.0.0.0"
MANAGEMENT_PORT := 5000

MINIO_ENDPOINT ?= 'http://127.0.0.1:9000'

.PHONY: install build run tag push style

install:
	pip install -r requirements.txt
	pip install -e .

build:
	docker build --build-arg HTTP_PROXY=$(HTTP_PROXY) --build-arg HTTPS_PROXY=$(HTTPS_PROXY) -f Dockerfile -t $(IMAGE):$(TAG) .

run:
	docker run -d -e HOSTNAME=$(MANAGEMENT_HOSTNAME) -e PORT=$(MANAGEMENT_PORT) -p $(MANAGEMENT_PORT):$(MANAGEMENT_PORT) \
	-e MINIO_ENDPOINT_ADDR=$(MINIO_ENDPOINT) -e MINIO_SECRET_ACCESS_KEY=$(MINIO_SECRET_ACCESS_KEY) -e MINIO_ACCESS_KEY_ID=$(MINIO_ACCESS_KEY_ID) \
	\$(TAG) /management/run.sh

tag:
	docker tag $(IMAGE):$(TAG) gcr.io/constant-cubist-173123/$(IMAGE)-$(TAG)

push:
	gcloud docker -- push gcr.io/constant-cubist-173123/$(IMAGE)-$(TAG)

style:
	flake8 --max-line-length 81


