#!/usr/bin/env bash

kubectl delete daemonsets,replicasets,deployments,pods,rc,jobs,ns,svc,secrets --all
helm delete --purge `helm ls | grep inferno | awk '{print($1)}'`
