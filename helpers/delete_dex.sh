#!/usr/bin/env bash

DEX=`kubectl get svc | grep dex | awk '{print $1}'`
kubectl delete service $DEX
kubectl delete deployment $DEX
