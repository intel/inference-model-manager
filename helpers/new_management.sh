#!/usr/bin/env bash

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
