#!/usr/bin/env bash

kubectl logs `kubectl get pods | grep management | awk '{print $1}'` -f