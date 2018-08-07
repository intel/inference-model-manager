FROM python:3.6

ENV PORT=5000
ENV HOSTNAME=0.0.0.0
ENV WORKERS=4
COPY . /management
WORKDIR /management

RUN pip install .

ENTRYPOINT gunicorn -w $WORKERS -k gevent -b $HOSTNAME:$PORT management_api.main:app

