#!/bin/bash
function fill_template() {
PATTERN=$1
REPLACEMENT=$2
FILE=$3
CMD="${SED_CMD}  -i s@$PATTERN@$REPLACEMENT@g $FILE" && echo "$CMD" && `$CMD`
}
