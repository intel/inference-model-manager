#
# Copyright (c) 2019 Intel Corporation
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

IMAGE ?= management-api
TAG ?= latest

MANAGEMENT_HOSTNAME := "0.0.0.0"
MANAGEMENT_PORT := 5000

MINIO_ENDPOINT ?= 'http://127.0.0.1:9000'

.PHONY: install docker_build docker_run docker_tag docker_push style circleci

install:
	pip install -r requirements.txt
	pip install -e .

docker_build:
	docker build --build-arg HTTP_PROXY=$(HTTP_PROXY) --build-arg HTTPS_PROXY=$(HTTPS_PROXY) -f Dockerfile -t $(IMAGE):$(TAG) .

docker_run:
	docker run -d -e HOSTNAME=$(MANAGEMENT_HOSTNAME) -e PORT=$(MANAGEMENT_PORT) -p $(MANAGEMENT_PORT):$(MANAGEMENT_PORT) \
    -e MINIO_ENDPOINT_ADDR=$(MINIO_ENDPOINT) -e MINIO_SECRET_ACCESS_KEY=$(MINIO_SECRET_ACCESS_KEY) -e MINIO_ACCESS_KEY_ID=$(MINIO_ACCESS_KEY_ID) \
    \$(TAG) /management/run.sh

docker_tag:
	docker tag $(IMAGE):$(TAG) gcr.io/constant-cubist-173123/$(IMAGE):$(TAG)

docker_push:
	gcloud docker -- push gcr.io/constant-cubist-173123/$(IMAGE):$(TAG)

style:
	flake8 --max-line-length 100 management_api/ test/

circleci: docker_build docker_tag docker_push

