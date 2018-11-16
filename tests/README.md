## Management API testing
It is possible to check if platform is working properly by running tests. 

### Prerequisities 

To run tests you need to create virtual environment:
```shell
$ python3 -m venv .venv
$ . .venv/bin/activate
$ pip install -r requirements.txt
```
### Run tests

Simplest way to run tests against the platform is by script provided:
```
./run_test.sh
``` 

#### Certificates
If you use self-signed certificates for platform you have to install your CA and pass to python interpreter.
For example for Ubuntu you could do something like this:
```
sudo cp <path_to_ca_file> /usr/local/share/ca-certificates/<ca_file_name>
sudo update-ca-certificates
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
