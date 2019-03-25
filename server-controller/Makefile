#
# Copyright (c) 2018-2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

all: docker

VERSION := $(shell git describe --tags --always --dirty)

IMAGE ?= server-controller-prod
TAG ?= latest

HTTP_PROXY := "$(http_proxy)"
HTTPS_PROXY := "$(https_proxy)"

docker_build:
	docker build --build-arg http_proxy=$(HTTP_PROXY) --build-arg https_proxy=$(HTTPS_PROXY) -f Dockerfile.prod -t $(IMAGE):$(TAG) .

lint:
	gometalinter --config=lint.json .
	gometalinter --config=lint.json ./apis/...

check-coverage:
	./check_coverage.sh

test: lint
	go test --cover .
	go test --cover ./apis/cr/v1

install-linter:
	go get -u github.com/alecthomas/gometalinter
	gometalinter --install

code-generation:
	deepcopy-gen --input-dirs=github.com/IntelAI/inference-model-manager/server-controller/apis/cr/v1/...

docker_tag:
	@ echo "tagging image"
	docker tag $(IMAGE):$(TAG) gcr.io/constant-cubist-173123/$(IMAGE):$(TAG)

docker_push:
	@ echo "pushing container to gcr.io"
	gcloud docker -- push gcr.io/constant-cubist-173123/$(IMAGE):$(TAG)

circleci: docker_build docker_tag docker_push
