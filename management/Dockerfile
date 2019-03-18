FROM clearlinux:latest

RUN swupd bundle-add python3-basic
RUN rm -fr /run/lock/clrtrust.lock
RUN clrtrust generate

ENV WORKERS=4

COPY . /management
WORKDIR /management

RUN pip --no-cache-dir install .

ENV REQUESTS_CA_BUNDLE=/var/cache/ca-certs/compat/ca-roots.pem

RUN useradd management-api-runner

EXPOSE 9443
ENTRYPOINT ./install_CA.sh && su management-api-runner -c "gunicorn --certfile=/certs/tls.crt --keyfile=/certs/tls.key -w $WORKERS -k gevent --bind 0.0.0.0:9443 management_api.runner:app" -
