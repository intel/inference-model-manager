DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
. $DIR/messages.sh

function wait_for_pod() {
  seconds=$1      
  pod_prefix=$2
  namespace=$3
  for (( i = $seconds; $i > 0; i=$i -1)); do
       ready=`kubectl get pods -n $namespace|grep $pod_prefix|grep "Running"|grep -v "0/"`
       if [ ! -z "$ready" ]
       then
         return 
       fi
       sleep 1
       print_ne "\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r $i seconds left" 
  done
  failure "Could not found pod with prefix: $pod_prefix, aborting"
  exit 1
}

