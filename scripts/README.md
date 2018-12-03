## Scripts

### Authenticate
**WARNING**:
If you use self-signed certificate you have to pass path to ca-cert file to scripts using ```--ca_cert``` flag.
You can obtain that certificate from you platform admin.
A special script for authentication has been created, it is available under the path:
```
webbrowser_authenticate.py
```
It runs the appropriate page for authentication in the browser, then after the correct login it saves the token and refresh token to the file.
By default this is the path `~/.imm`.
This path can be changed by setting the `IMM_CONFIG_PATH` environment variable.  
Command to run the script:

```
python webbrowser_authenticate.py --address <ip_to_management_api>
```
It works with both python versions.  
By default, management_api runs on port 443 and this port is used in this script. To change this, add another flag when you start the script:
```
python webbrowser_authenticate.py --address <management_api ip> --port <management_api port>
```

### Management API calls
*api_call.sh* script allows to call Management API in a more convinient way.    

#### List of available options
##### login
  - Additional parameters provided with environment variables: cert with MANAGEMENT_CA_CERT_PATH
  - Usage example:
    ```
    ./api_call.sh -a mgmt.example.com login
    ```
##### logout
  - Usage example:
    ```
    ./api_call.sh logout
    ```
##### create (c)
- tenant (t)
  - Required parameters: tenantName, scope (group name)
  - Additional parameters provided with environment variables: cert with CERT env, quota with TENANT_RESOURCES env
  - Usage example:
    ```
    ./api_call.sh create tenant mytenant users
    ```
- endpoint (e)
  - Required parameters: endpointName, modelName, modelVersion, tenantName, subjectName (default: client)
  - Additional parameters provided with environment variables: quota with ENDPOINT_RESOURCES env
  - Usage example:
    ```
    ./api_call.sh create e myendpoint mymodel 1 mytenant 
    ```
##### remove (rm)
- tenant (t)
  - Required parameters: tenantName
  - Usage example:
    ```
    ./api_call.sh rm t mytenant
    ```
- endpoint (e)
  - Required parameters: endpointName, tenantName
  - Usage example:
    ```
    ./api_call.sh rm e myendpoint mytenant
    ```
- model (m)
  - Required parameters: modelName, modelVersion, tenantName
  - Usage example:
    ```
    ./api_call.sh rm m mymodel 2 mytenant
    ```
##### list (ls)
- tenants (tenant / t)
  - Usage example:
    ```
    ./api_call.sh ls t
    ```
- endpoints (endpoint / e)
  - Required parameters: tenantName
  - Usage example:
    ```
    ./api_call.sh ls e mytenant
    ```
- models (model / m)
  - Required parameters: tenantName
  - Usage example:
    ```
    ./api_call.sh ls m mytenant
    ```
##### update (up)
- endpoint
  - Required parameters: endpointName, modelName, modelVersion, tenantName
  - Usage example:
    ```
    ./api_call.sh up myendpoint mymodel 2 mytenant
    ```
##### scale (s)
- endpoint
  - Required parameters: endpointName, replicas, tenantName
  - Usage example:
    ```
    ./api_call.sh s myendpoint 5 mytenant
    ```
##### upload (u)
  - Required parameters: path_to_model, modelName, modelVersion (default: 1), tenantName
  - Usage example:
    ```
    ./api_call.sh u ../model.pb mymodel 1 mytenant 
    ```
##### run-inference (ri)
  - Required parameters: grpc_address, modelName, input_type (numpy/list), input_path, batch_size, server_cert_path, client_cert_path, client_key_path
  - Usage example:
    ```
    ./api_call.sh ri myendpoint-mytenant.example.com:443 mymodel numpy ../images.npy  10 ../server-tf.crt ../client-tf.crt ../client-tf.key
    ```
    
#### Environment variables
- `IMM_CONFIG_PATH` - Inference Model Manager config file, default: `~/.imm`
- `MANAGEMENT_API_ADDRESS` - management api address, can be provided with `-a` option, default: `127.0.0.1`
- `MANAGEMENT_API_PORT` - management api port, can be provided with `-p` option, default: `443`
- `CERT` - path to certificate for tenant creation, **required**
- `MANAGEMENT_CA_CERT_PATH` - path to ca-man-api.crt used for login
- `TENANT_RESOURCES` - quota used for tenant creation, default: `"{\"requests.cpu\": \"2\", \"requests.memory\": \"2Gi\", \"limits.cpu\": \"2\", \"limits.memory\": \"2Gi\", \"maxEndpoints\": 15}"`
- `ENDPOINT_RESOURCES` - quota used for endpoint creation, default: `"{\"requests.cpu\": \"1\", \"requests.memory\": \"1Gi\", \"limits.cpu\": \"1\", \"limits.memory\": \"1Gi\"}"`

More information: `./api_call.sh -h`.
More info: `./api_call.sh -h`


### Uploading a model
Recommended way to upload models is to use `model_upload_cli.py` script.  
Example:
```
python model_upload_cli.py model-name model-version tenant-name
```
More info: `python model_upload_cli.py -h`
