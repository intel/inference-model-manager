function header() {
TEXT="$1"
YELLOW='\033[1;33m'
NC='\033[0m' # No Color
printf "${YELLOW}$TEXT${NC}\n"
}

function action_required() {
TEXT="$1"
BOLD_YELLOW='\033[1;31m'
NC='\033[0m' # No Color
printf "${BOLD_YELLOW}ACTION_REQUIRED: $TEXT${NC}\n"
}


function success() {
TEXT="$1"
GREEN='\033[0;32m'
NC='\033[0m' # No Color
printf "${GREEN}$TEXT${NC}\n"
}


function print_ne() {
TEXT="$1"
CYAN='\033[0;36m'
NC='\033[0m' # No Color
echo -ne "${CYAN}$TEXT${NC}"       
}

function failure() {
TEXT="$1"
RED='\033[0;31m'
NC='\033[0m' # No Color
printf "${RED}$TEXT${NC}\n"
}

function show_result() {
RESULT="$1"
SUCCESS_MSG="$2"
FAIL_MSG="$3"
if [ "$RESULT" -eq 0 ]; then
    success "$SUCCESS_MSG"
else
    failure "$FAIL_MSG"
fi        
}


