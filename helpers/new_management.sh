#!/usr/bin/env bash
#
# Copyright (c) 2018 Intel Corporation
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

# Requirements: management.yaml in home directory with management-api deployment
# Run from management catalog
# Ensure that IMAGE and TAG are the same as in deployment yaml

cd ~/inferno-platform/management
git pull
kubectl delete deployment management-api
export IMAGE=management-api
export TAG=latest
make circleci
kubectl create -f ~/management.yaml
chmod +x ../tests/*.sh
chmod +x ../helpers/*.sh
