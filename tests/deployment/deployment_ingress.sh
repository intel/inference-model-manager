#!/usr/bin/env bash
RETURN_DIR=$PWD
if [ "$ING_CERTS" = "true" ]
then
echo "Generate all certs required to run platform"
cd ../../helm-deployment/ing-subchart/certs/ && ./scriptcert.sh
cd $RETURN_DIR
fi
if [ "$WRONG_CERTS" = "true" ]
then
echo "Generate certs required for tests"
cd ../../helm-deployment/ing-subchart/certs/ && ./script-wrong-certs.sh
cd $RETURN_DIR
fi
cd $RETURN_DIR
helm install ../../helm-deployment/ing-subchart/
