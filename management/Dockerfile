FROM python:3.6

ENV WORKERS=4
COPY . /management
WORKDIR /management

RUN pip install .
EXPOSE 443
ENTRYPOINT gunicorn --certfile=/certs/tls.crt --keyfile=/certs/tls.key -w $WORKERS -k gevent --bind 0.0.0.0:443 management_api.runner:app
