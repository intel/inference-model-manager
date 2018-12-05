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


#### Usage
Run help `python grpc_client --help`: 

```
usage: grpc_client.py [-h] [--server_cert SERVER_CERT]
                      [--client_cert CLIENT_CERT] [--client_key CLIENT_KEY]
                      (--images_numpy_path IMAGES_NUMPY_PATH | --images_list IMAGES_LIST)
                      [--target_name TARGET_NAME] [--input_name INPUT_NAME]
                      [--output_name OUTPUT_NAME] [--image_size IMAGE_SIZE]
                      [--images_number IMAGES_NUMBER]
                      [--batch_size BATCH_SIZE] [--no-ssl] [--transpose_input]
                      [--no_imagenet] [--performance]
                      grpc_address model_name

Do requests to Tensorflow Serving using jpg images or images in numpy format

positional arguments:
  grpc_address          Specify url:port to gRPC service
  model_name            Specify model name, must be same as is in service

optional arguments:
  -h, --help            show this help message and exit
  --server_cert SERVER_CERT
                        Path to server certificate
  --client_cert CLIENT_CERT
                        Path to client certificate
  --client_key CLIENT_KEY
                        Path to client key
  --images_numpy_path IMAGES_NUMPY_PATH
                        Numpy in shape [n,w,h,c]
  --images_list IMAGES_LIST
                        Images in .jpg format
  --target_name TARGET_NAME
                        Specify to override target name
  --input_name INPUT_NAME
                        Input tensor of model. Default: in
  --output_name OUTPUT_NAME
                        Output tensor of model. Default: out
  --image_size IMAGE_SIZE
                        Size of images. Default: 224
  --images_number IMAGES_NUMBER
                        Define number of images to inference. Specify if you
                        want to use only part of numpy array
  --batch_size BATCH_SIZE
                        Number of images in a single request. Default: 1
  --no-ssl              Set for non-SSL calls
  --transpose_input     Set to make NCHW->NHWC input transposing
  --no_imagenet         Set for non-Imagenet datasets
  --performance         Enable processing performance info

```


#### Example command
```
python grpc_client.py <endpoint_address> model-name --images_list <image.jpg> \
--server_cert <path_to_server_cert> --client_cert <path_to_client_cert> --client_key <path_to_client_key>
```

#### Performance information
With `--performance` flag enable performance information.

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
