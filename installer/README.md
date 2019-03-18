# Installation

## Prerequisites
* python3.6
* virtualenv ```pip install virtualenv```
* [yq](https://github.com/mikefarah/yq) *(Use this specific version of yq)*
* [jq](https://stedolan.github.io/jq/)
* [helm](https://github.com/helm/helm)
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
* [kops](https://github.com/IntelAI/inference-model-manager/tree/master/kops) or other tool for
  creating k8s cluster (if needed)
* unbuffer
  * ubuntu: `sudo apt-get install expect-dev` or `sudo apt-get install expect`
  * for mac it is downloaded during installation
* `export GOOGLE_APPLICATION_CREDENTIALS` if using kops (or use -g switch)  
* domain for IMM

On Ubuntu, you can use script to install dependencies
`./prerequisites_ubuntu.sh`

* Install required dependencies:
  ```
    cd inference-model-manager
    virtualenv -p python3.6 .venv
    . .venv/bin/activate
    pip install -q --upgrade pip &&  pip install -q -r tests/requirements.txt && pip install -q -r scripts/requirements.txt
  ```
  * if using AWS Route53 please install awscli:
    ```
	  pip install -q awscli --upgrade
	```
## DNS hook (optional)
* For deployment automation, you can provide script which will setup the DNS for IMM cluster.
  Place the script in `./hooks/dns_entry_hook.sh`. 
  See `./hooks/example_dns_entry_hook.sh`
* If you don't provide DNS hook script, you will be asked to create DNS entry during installation.

## Run
Additional options
    -z - GCE cluster zone (if using kops and GCE)
    -q - silent mode (shows only important logs)
    -s - skip cluster creation via kops
    -p - set proxy (address:port)
    -A - set minio access key
    -S - set minio secret key
    -h/? - show help
Usage examples
    install.sh -k <name> -d <domain>
    install.sh -k <name> -d <domain> -z <gce_zone>
    install.sh -k <name> -d <domain> -s -q
* Required optons:
  * `-k` - cluster name
  * `-d` - domain name
* Additional options
  * `-z` - GCE cluster zone (if using kops and GCE)
  * `-q` - silent mode (shows only important logs)
  * `-s` - skip cluster creation via kops 
  * `-g` - GCE user name (usually email), used to create cluster in GCE
  * `-p` - set proxy (address:port)
  * `-A` - set minio access key
  * `-S` - set minio secret key
  *  -t  - set single tenant mode and use Management API authorization instead of Kubernetes authorization
           (use this option if it's not possible to restart kubernetes API, for 
           example in GKE cluster)
  * `-h/?` - show help
* Usage examples
  * Installation with `kops` 
  * `./install.sh -k <name> -d <domain>`
  * Installation on GCE with `kops` (user must be logged with `gcloud auth login`)
  * `./install.sh -k <name> -d <domain> -z <gce_zone> -g john.doe@example.com`
  * Installation on existing kubernetes cluster ( requires access to existing kubernetes via `kubectl` )
  * `./install.sh -d <domain> -s`
  * Installation on GCE with `kops` using custom Minio access key and secret key and with proxy
  * `./install.sh -k <name> -d <domain> -s -q -p <proxy_address:port> -A <minio_access_key> -S <minio_secret_key>`
  * Installation on existing GKE kubernetes cluster
  * `./install.sh -d <domain> -s`-t
### Update DNS records for new domain
#### Using AWS Route53
* set up [awscli](https://aws.amazon.com/cli/)
* ```aws configure```
* create
```
cd utils/route53
./apply.sh CREATE $IP_ADDRESS $DOMAIN_NAME
```
* delete
```
cd utils/route53
./apply.sh DELETE $IP_ADDRESS $DOMAIN_NAME
```
## Single Tenant mode
Single Tenant mode will create tenant which will be default tenant to use while interacting with platform. It has well-known name `default-tenant`.

## Tests
* Prerequisites:
  * python3.6 or higher
  * activated virtualenv (described in the Prerequisites section)
* Run:
  ```
  . validate.sh <domain_name> 
  ```
  * using proxy
  ```
  . validate.sh <domain_name> <proxy_with_port>
  ```
* Troubleshooting
  * ```
	Get admin token
	  File "../tests/management_api_tests/authenticate.py", line 110
	user_password = f'{userpass}_pass'
	SyntaxError: invalid syntax 
    ```
      This problem occurs when you run tests outside virtualenv.
      Please check *Install required dependencies* in **Prerequisites** section.
