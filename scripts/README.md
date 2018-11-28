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
To make usage of platform simpler, it is `api_call.sh` presented, which will allow to make calls to 
API in more convenient way.  
Usage examples:
```
./api_call.sh create tenant <tenant_name>
./api_call.sh create endpoint <endpoint_name> <model_name>
./api_call.sh rm tenant <tenant_name>
./api_call.sh rm endpoint <endpoint_name>
./api_call.sh update endpoint <endpoint_name> <new_model_name>
./api_call.sh scale endpoint <endpoint_name> <replicas>
./api_call.sh -a 127.0.0.1 -p 5555 login
./api_call.sh logout
./api_call.sh ls endpoints <tenant_name>
./api_call.sh upload <model_path> <model_name> <model_version> 
./api_call.sh ri <grpc_address> <grpc_port> <input_type:list/numpy> <input> <batch_size> <model_name>
```
More info: `./api_call.sh -h`


### Uploading a model
Recommended way to upload models is to use `model_upload_cli.py` script.  
Example:
```
python model_upload_cli.py model-name model-version tenant-name
```
More info: `python model_upload_cli.py -h`
