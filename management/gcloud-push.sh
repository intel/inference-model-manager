export TAG=$(shell hashdeep -r -b . | md5sum | tr -d '-' | tr -d ' ')
make circleci
