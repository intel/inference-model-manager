# inferno-platform
source code, deployment automation and tests for inference platform POC made for Blizzard

## management
### management-api
* `export MANAGEMENT_HOSTNAME=0.0.0.0`
* `export MANAGEMENT_PORT=[port]`
* `export MINIO_ENDPOINT=[minio_endpoint]`

* `export IMAGE=<management-api image name>` (default: management-api)
* `export TAG=<management-api tag>` (default: latest)


Run these commands from `management` catalog in order to build docker image or run management api with docker
* `make build`
* `make run`

If you run Docker container with API locally, you need to copy your $HOME/.kube/config with credentials to particular cluster to management folder.

#### local development
* create virtualenv (`virtualenv .venv`)
* activate virtualenv (`. .venv/bin/activate`)
* install dependencies (`make install`)
* run minio server (`minio server /data`) (OPTIONAL: '--address: ":minio-port")
* get minio accessKey and secretKey from ~/.minio/config.json (that's default location for minio config file, updated after minio server run), you can use
helpers/get_minio_credentials.sh)
  * get_minio_credentials.sh gets accessKey and secretKey from `~/.minio/config.json` and exports these to `MINIO_ACCESS_KEY_ID` and
  `MINIO_SECRET_ACCESS_KEY`:
    ```
    . helpers/get_minio_credentials.sh
    ```
* run (`management-api`)

### k8s deployment
* `make build` - build docker image
* `make tag` - tag image
* `make push` - push image to grc
* update MINIO_ACCESS_KEY and MINIO_SECRET_KEY with proper values (in kubernetes/minio.yaml)
* `kubectl create -f kubernetes/minio.yaml` - create minio deployment
* using `kubectl get svc` get minio's external_ip 
* update MINIO_ENDPOINT in kubernetes/management.yaml with minio's external_ip (remember about http:// at the beginning and port at the end)
* update MINIO_ACCESS_KEY and MINIO_SECRET_KEY with proper values(in kubernetes/management.yaml)
* `kubectl create -f kubernetes/management.yaml`
* get external_ip of management-api (with `kubectl get svc`)
* test k8s deployment with example provided below (remember to change localhost to management-api's external_ip)

### example
* create new tenant: 
```
curl -X POST "http://localhost:8000/tenants" -H "accept: application/json" -H "Authorization: <jwt_token>" \
-H "Content-Type: application/json" -d "{\"name\": \"tenantname\", \"cert\":\"cert_path\", \"scope\":\"scope_name\"}"
```

