# Building docker images for Inference Model Manager

## TensorFlow Serving
The choice is to use prebuilt Docker images published by Google on [Dockerhub](https://hub.docker.com/r/tensorflow/serving/) 
or to build them from sources with compilation options optimized for target HW and CPU architecture on the Kubernetes nodes.
Description how to build Tensorflow Serving from sources are 
[https://www.tensorflow.org/serving/setup](https://www.tensorflow.org/serving/setup)
Tensorflow Serving can be built with Eigen backend libraries (default option) or with MKL libraries.
MKL backed in TF Serving brings better performance but needs threading parameters tuning via setting environment variables.

Support for model servers templates with the option to define auxilary environment variables on model server containers
will be added to the IMM soon.


## CRD controller

Refer to the documentation on [server-controller](../server-controller) documentation.

# Management API server

Refer to the documentation on [management api](../management) documentation.

