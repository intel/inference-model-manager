#
# Copyright (c) 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#!/bin/bash

COVERAGE=`go test -cover | grep -oP '\d{1,3}(\.\d{1,4})?%' | sed 's/\%//g'`

check_coverage() {
if [ $(echo "$1 < 50" | bc) -ne 0 ]; then
        echo "Coverage is under 50%"
        return 1
fi
}

check_coverage $COVERAGE
