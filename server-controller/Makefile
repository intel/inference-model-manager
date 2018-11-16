all: docker

VERSION := $(shell git describe --tags --always --dirty)

IMAGE ?= server-controller-prod
TAG ?= latest

docker_build:
	docker build --build-arg http_proxy=$(HTTP_PROXY) --build-arg https_proxy=$(HTTPS_PROXY) -f Dockerfile.prod -t $(IMAGE):$(TAG) .

lint:
	gometalinter --config=lint.json .
	gometalinter --config=lint.json ./apis/...

test: lint
	go test --cover .
	go test --cover ./apis/cr/v1

code-generation:
	deepcopy-gen -v 3 --input-dirs=github.com/NervanaSystems/inferno-platform/server-controller/apis/cr/v1/...

docker_tag:
	@ echo "tagging image"
	docker tag $(IMAGE):$(TAG) gcr.io/constant-cubist-173123/$(IMAGE):$(TAG)

docker_push:
	@ echo "pushing container to gcr.io"
	gcloud docker -- push gcr.io/constant-cubist-173123/$(IMAGE):$(TAG)

circleci: docker_build docker_tag docker_push
