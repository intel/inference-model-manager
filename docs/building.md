# Building docker images for Inference Model Manager

## TensorFlow Serving
The choice is to use prebuilt Docker images published by Google on [Docker Hub](https://hub.docker.com/r/tensorflow/serving/) 
or to build them from sources with compilation options optimized for target HW and CPU architecture on the Kubernetes nodes.
Description how to build Tensorflow Serving from sources are 
[https://www.tensorflow.org/serving/setup](https://www.tensorflow.org/serving/setup)
Tensorflow Serving can be built with Eigen backend libraries (default option) or with MKL libraries.
MKL backed in TF Serving brings better performance but needs threading parameters tuning via setting environment variables.

## OpenVINO Model Server
The choice is to use prebuilt Docker image published by Intel on [Docker Hub](https://hub.docker.com/r/intelaipg/openvino-model-server/) 
or to [build the image](https://github.com/IntelAI/OpenVINO-model-server/blob/master/docs/docker_container.md) yourself

## CRD controller
Prebuilt images are avaliable in https://hub.docker.com/r/intelaipg/inference-model-manager-crd

If you want to build them on your own, please refer to the documentation on [server-controller](../server-controller) documentation.

## Management API server
Prebuilt images are avaliable in https://hub.docker.com/r/intelaipg/inference-model-manager-api

If you want to build them on your own, please refer to the documentation on [management api](../management) documentation.

