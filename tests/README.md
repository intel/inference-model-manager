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



#### Management testing

* export MANAGEMENT_API_URL=http://<url>:5000/tenants
* export MINIO_SECRET_KEY='<key>' (remember about ' chars)
* export MINIO_ACCESS_KEY='<key>' (remember about ' chars)
* export MINIO_ENDPOINT_ADDR=http://<minio_ip>:9000
* pytest -v .

* you can check how to get required values in get_test_envs.sh script

!WARNING
If you use self-signed certificates for platform you have to install your CA and pass to python interpreter.
For example for Ubuntu you could do something like this:
```
sudo cp <path_to_ca_file> /usr/local/share/ca-certificates/<ca_file_name>
sudo update-ca-certificates
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
