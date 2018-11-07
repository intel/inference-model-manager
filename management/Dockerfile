FROM python:3.6

ENV WORKERS=4
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
COPY . /management
WORKDIR /management

RUN pip install .
EXPOSE 443
ENTRYPOINT ./install_CA.sh && gunicorn --certfile=/certs/tls.crt --keyfile=/certs/tls.key -w $WORKERS -k gevent --bind 0.0.0.0:443 management_api.runner:app
