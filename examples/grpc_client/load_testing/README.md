# Load Test

## Prerequisites
* Python 3.6
* Install [requirements](../requirements.txt) needed to launch [grpc client](../README.md)
* Install Locust requirements ```pip install -r requirements-locust.txt```


## Description
Script available under this directory allow users to execute on their own load tests. Prepared [Locust class](image_locust.py)
on start loads environment variables and images also create grpc stub. In hatching phase this client only perform request to GRPC service using earlier loaded images. 
Size of request batch is configurable by setting

## Configurable parameters
````
    GRPC_ADDRESS # address to grpc endpoint
    MODEL_NAME = # model name; default value=resnet
    TENSOR_NAME # input tensor name' default value=in
    IMAGES # path to images, separated by comma; example=/test/image.jpeg,/test/image2.jpeg
    SERVER_CERT # path to server certificate
    CLIENT_CERT # path to client certificate
    CLIENT_KEY # path to client key
    TRANSPOSE # set to True if you want to transpose input or completly unset env to not transpose
    TIMEOUT # timeout used in grpc request; default value=10.0
````

## Start Locust

A script was prepared to launch specific amount of locust instances, by passing integer to bash script. 
Without passing any parameter script will launch Locust in distributed mode with 2 slaves.
If you want to perform as many RPS as possible we recommend to spawn 1 slave for 1 CPU core.
Also this script creates temporary file `pid_locust` which keep PID of processes launched by this script.

```./start_locust.sh```

Examples:
```
   ./start_locust.sh 1 # Launch Locust in distributed mode with 1 slave
   ./start_locust.sh 0 # Launch Locust in single instance mode
   ./start_locust.sh 4 # Launch Locust in distributed mode with 4 slaves
```

After using this command Locust will be available under [http://localhost:8089](http://localhost:8089)

## Stop Locust

We run all instances as background process, so to stop load tests you can use our script ```./stop_locust```
, which also remove temporary file created earlier or read PIDs in `pid_locust` file and simply kill processes listed in that file.
