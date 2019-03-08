#!/bin/bash
SLAVES=${1:-2}

if [ "$SLAVES" == "0" ]
then
  LOCUST_OPTS=""
  echo "Launch locust single instance"
else
  LOCUST_OPTS="--master"
  echo "Launch locust master"
fi

locust -f image_locust.py ${LOCUST_OPTS} &
echo $! >> pid_locust
for (( c=1; c<=$SLAVES; c++ ))
do
   echo "Launch locust slave $i"
   locust -f image_locust.py --master-host=localhost --slave &
   echo $! >> pid_locust
done
