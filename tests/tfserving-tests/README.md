## Tests for Tensorflow Serving

#### Testing

You need to specify URL under which endpoint with model is given. To do that, edit config.py:
```shell
import os

HOST_NAME = os.environ.get('HOST_NAME', <your-host-name>)
HOST_PORT = os.environ.get('HOST_PORT', <your-port-number>)
```
To create test environment run:
```shell
$ chmod +x create_testenv.sh
$ ./create_testenv.sh
```
To run tests run these commands:
```shell
$ chmod +x run_test.sh
$ ./run_tests.sh
```
To delete test environment run:
```shell
$ chmod +x delete_testenv.sh
$ ./delete_testenv.sh
```

#### Development tips

Note that tests are written in Python 2.7.

