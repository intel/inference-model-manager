#!/usr/bin/env bash

cp /dex-CA/ca.crt /usr/local/share/ca-certificates/dex-ca.crt
update-ca-certificates
