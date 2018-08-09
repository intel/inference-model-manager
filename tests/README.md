#### Testing

You need to specify URL under which endpoint with model is given. To do that, edit conftest.py:
```shell
import os

TFSERVING_HOST_NAME = os.environ.get('HOST_NAME', <your-host-name>)
TFSERVING_HOST_PORT = os.environ.get('HOST_PORT', <your-port-number>)
```
To run tests you need create virtual environment:
```shell
$ python3 -m venv .venv
$ . .venv/bin/activate
$ pip install -r requirements.txt
```
