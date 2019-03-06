## Scripts

__Note:__ To use all features of imm you need to install packages from requirements with
```pip install -r requirements.txt```, if you don't have them already.


### Authenticate
**WARNING**:
If you use self-signed certificate you have to pass path to ca-cert file to scripts using ```--ca_cert``` flag.
You can obtain that certificate from you platform admin.
A special script for authentication has been created, it is available under the path:
```
webbrowser_authenticate.py
```
It runs the appropriate page for authentication in the browser, then after the correct login it saves the token and refresh token to the file.
By default this is the path `~/.immconfig`.
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

**Handling proxy**

If you are behind proxy, use extra proxy parameters:

```
--proxy_host <host> --proxy_port <port>
```

**Login without launching browser**

If your machine does not provide any web-browser or you are using it over ssh, you can try our "out of browser" option. 
To use this mode please add parameter:

```
--offline
```

### Management API calls
*imm* script allows to call Management API in a more convenient way.

#### List of available options
##### login
  - Additional parameters: --proxy_host, --proxy_port
  - Additional parameters provided with environment variables: certificate path with 
      MANAGEMENT_CA_CERT_PATH
  - Usage example:
    ```
    ./imm -a mgmt.example.com login
    ```
  - Using proxy and offline login option:
    ```
    ./imm -o login --proxy_port 911 --proxy_host example.proxy.com
    ```
##### logout
  - Usage example:
    ```
    ./imm logout
    ```
##### create (c)
- tenant (t)
  - Required parameters: tenantName, scope (group name)
  - Additional parameters provided with environment variables: base64 encoded certificate with 
      CERT env (**required**), quota with TENANT_RESOURCES env
  - Usage example:
    ```
    ./imm create tenant mytenant users
    ```
- endpoint (e)
  - Required parameters: endpointName, modelName, modelVersionPolicy, tenantName, servingName, subjectName (default: client)
  - Additional parameters provided with environment variables: quota with ENDPOINT_RESOURCES env
  - Usage example:
    ```
    ./imm create e myendpoint mymodel "{specific {versions: 1} }" mytenant tf-serving
    ```
##### remove (rm)
- tenant (t)
  - Required parameters: tenantName
  - Usage example:
    ```
    ./imm rm t mytenant
    ```
- endpoint (e)
  - Required parameters: endpointName, tenantName
  - Usage example:
    ```
    ./imm rm e myendpoint mytenant
    ```
- model (m)
  - Required parameters: modelName, modelVersion, tenantName
  - Usage example:
    ```
    ./imm rm m mymodel 2 mytenant
    ```
##### list (ls)
- tenants (tenant / t)
  - Usage example:
    ```
    ./imm ls t
    ```
- endpoints (endpoint / e)
  - Required parameters: tenantName
  - Usage example:
    ```
    ./imm ls e mytenant
    ```
- models (model / m)
  - Required parameters: tenantName
  - Usage example:
    ```
    ./imm ls m mytenant
    ```
- servings (serving | s)
  - Usage example:
  ```
  ./imm ls s
  ```
##### update (up)
- endpoint
  - Required parameters: endpointName, tenantName
  - Optional parameters: --modelName, --modelVersionPolicy, --resources, --subjectName
  - Usage example:
    ```
    ./imm up e myendpoint mytenant --modelVersionPolicy "{specific{versions:2}}"
    ./imm up e myendpoint mytenant --resources "{\"requests.cpu\":\"0\",\"requests.memory\":\"0\"}"
    ./imm up e myendpoint mytenant --modelName newmodel --subjectName newsubject
    ```
##### scale (s)
- endpoint
  - Required parameters: endpointName, replicas, tenantName
  - Usage example:
    ```
    ./imm s myendpoint 5 mytenant
    ```
##### upload (u)
  - Required parameters: path_to_model, modelName, modelVersion (default: 1), tenantName
  - Usage example:
    ```
    ./imm u ../model.pb mymodel 1 mytenant 
    ```
##### run-inference (ri)
  - Required parameters: grpc_address, modelName, input_type (numpy/list), input_path, batch_size, server_cert_path, client_cert_path, client_key_path
  - Optional parameters: --input_name, --transpose_input, --output_name
  - Usage example:
    ```
    ./imm ri myendpoint-mytenant.example.com:443 mymodel numpy ../images.npy  10 ../server-tf.crt ../client-tf.crt ../client-tf.key
    ```
    or with optional parameters:
    ```
    ./imm ri myendpoint-mytenant.example.com:443 mymodel numpy ../images.npy  10 ../server-tf.crt ../client-tf.crt ../client-tf.key --input_name input --transpose_input --output_name output
    ```
    In order to run inference on images (with `list` as `input_type`) you need to provide list of
     paths to those images like:
     ```
     ./imm ri myendpoint-mytenant.example.com:443 mymodel list "cat.jpg, dog.jpg, fish.jpg"  3 ../server-tf.crt ../client-tf.crt ../client-tf.key
     ```

##### view (v)
- endpoint
  - Required parameters: endpointName, tenantName
  - Usage example:
    ```
    ./imm v e myendpoint mytenant
    ```
- serving
  - Required parameter: servingName
  - Usage example:
    ```
    ./imm v s myserving
    ```
  - To make result more readable we recommend using [yq](https://yq.readthedocs.io/en/latest/#synopsis)
    - Usage example:
    ```
    ./imm v s ovms | yq -y '.'
    ```

##### get (g)
- model-status (ms)
  - **Currently available only for endpoints with tf-serving**
  - Required parameters: grpc_address, modelName, server_cert_path, client_cert_path, client_key_path 
  - Usage example:
    ```
    ./imm g ms myendpoint-mytenant.example.com:443 mymodel ./server-tf.crt ./client-tf.crt ./client-tf.key 
    ```

#### Environment variables
- `IMM_CONFIG_PATH` - Inference Model Manager config file, default: `~/.immconfig`
- `MANAGEMENT_API_ADDRESS` - management api address, can be provided with `-a` option, default: `127.0.0.1`
- `MANAGEMENT_API_PORT` - management api port, can be provided with `-p` option, default: `443`
- `CERT` - base64 encoded certificate for tenant creation, **required**
- `MANAGEMENT_CA_CERT_PATH` - path to .crt file with certificate used for login
- `TENANT_RESOURCES` - quota used for tenant creation, default: `"{\"requests.cpu\": \"2\", \"requests.memory\": \"2Gi\", \"limits.cpu\": \"2\", \"limits.memory\": \"2Gi\", \"maxEndpoints\": 15}"`
- `ENDPOINT_RESOURCES` - quota used for endpoint creation, default: `"{\"requests.cpu\": \"1\", \"requests.memory\": \"1Gi\", \"limits.cpu\": \"1\", \"limits.memory\": \"1Gi\"}"`
- `TOKEN` - token required to perform request, by default it is provided within `IMM_CONFIG_PATH` file

#### Options
- `v` - verbose mode, prints simplified cURL (vv - prints full cURL)
- `h` - help
- `a` - management api address (could be provided with MANAGEMENT_API_ADDRESS env or from config file)
- `p` - management api port (could be provided with MANAGEMENT_API_PORT env or from config file)
- `c` - path to config file
- `k` - allowing connection to management api endpoints with not trusted certificates


More information: `./imm -h`.

### Uploading a model
#### Single file
Upload single file.
 
Example:
```
python model_upload_cli.py model.pb model-name model-version tenant-name
```
#### Directory tree
Upload complex structure. Any directory structure is supported.

For example Tensorflow Serving's saved models have specific dir tree:
```
resnet/
    1/
        saved_model.pb
        variables/
            variables.data-0000-of-00001
            variables.index
``` 
Upload script will walk through dir tree until it finds first directory which contains more 
than one element (dir) inside. For example above, the upload will start on level of `saved_model.pb`
and `variables/`. Content will be uploaded to 
```
model-name/
    model-version/
```
where `model-name` and `model-version` are given as parameters.

For directory upload, pass a path to a directory:
```
python model_upload_cli.py dir-path model-name model-version tenant-name
```
Example:
```
python model_upload_cli.py resnet resnet-model 1 tenant
```
#### Tarballs
Passing tarballs to upload scripts is also possible. Script will extract tar file to `/tmp/imm` 
directory, after that the behaviour is the same as in directory or single file upload.

Example:
```
python model_upload_cli.py resnet_v2_fp16_savedmodel_NCHW.tar.gz resnet-model 1 tenant
```

More info: `python model_upload_cli.py -h`
