FROM clearlinux:latest

RUN swupd bundle-add python3-basic
RUN clrtrust generate

ENV WORKERS=4

COPY . /management
WORKDIR /management

RUN pip --no-cache-dir install .

ENV REQUESTS_CA_BUNDLE=/var/cache/ca-certs/compat/ca-roots.pem

EXPOSE 443
ENTRYPOINT ./install_CA.sh && gunicorn --certfile=/certs/tls.crt --keyfile=/certs/tls.key -w $WORKERS -k gevent --bind 0.0.0.0:443 management_api.runner:app
