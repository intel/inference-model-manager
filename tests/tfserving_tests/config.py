import os
TFSERVING_HOST_NAME = os.environ.get('HOST_NAME', "resnet.serving-service.com")
TFSERVING_HOST_PORT = os.environ.get('HOST_PORT', 443)
