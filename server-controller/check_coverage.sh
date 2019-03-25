#!/bin/bash
COVERAGE=`go test -cover | grep -oP '\d{0,2}(\.\d{1,4})?%'`

if [[ $COVERAGE < 50 ]]; then
        echo "Coverage is under 50%"
        exit 1
fi

