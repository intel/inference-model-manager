import os


HOST_NAME = os.environ.get('HOST_NAME', "serving-service.kube.cluster")
HOST_PORT = os.environ.get('HOST_PORT', 443)
