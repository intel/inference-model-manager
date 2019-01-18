# import from the same directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
. $DIR/messages.sh
function progress_bar() {
  seconds=$1      
  for (( i = $seconds; $i > 0; i=$i -1)); do
       sleep 1
       print_ne "\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r $i seconds left" 
  done
}


