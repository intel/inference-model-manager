#!/usr/bin/env bash
while read p; do
  kill -9 $p
done <pid_locust
echo "Now all locust instances have been killed"

rm pid_locust
