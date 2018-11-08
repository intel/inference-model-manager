## gRPC example client

Simple example client for inference on Resnet model 

#### Software requirements
You need Python 3.6. Create virtual environment:
```
virtualenv -p python3.6 .venv
```
Packages needed:
* tensorflow-serving-api
* Pillow
* numpy

To install, run:

```
pip install -r requirements.txt
```

### About

`grpc_client.py` allows to make requests to endpoint which contains served Resnet model. To use it, 
you need some images in .jpg format or numpy array in .npy format.  
Default setting is to use certificate validation. You can change this behaviour by specifying `--no-ssl` flag.  

#### Example command
```
python grpc_client.py --grpc_address <endpoint_address> --grpc_port 443 --endpoint_name <endpoint_name> --images_list <image.jpg> --model_name model-name --server_cert <path_to_server_cert> --client_cert <path_to_client_cert> --client_key <path_to_client_key>
```

Run help for more information about additional flags:
```
python grpc_client.py --help
```

#### Performance information
With `--performance` flag enable perfomance information.

##
## Create numpy array with images
You can provide list or directory containing Imagenet images to `images_2_numpy.py` script in order 
to create numpy array to feed `grpc_client.py`. That is not required step.

Note that this script doesn't provide preprocessing of data.

#### Example commands
```
python images_2_numpy.py --images_dir ./images --number_of_images 5 --output images.npy
```
```
python images_2_numpy.py --images_list image1.jpg,image2.jpg --image_size 224
```
Run help for more information about additional flags:
```
python images_2_numpy.py --help
```
