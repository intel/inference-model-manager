FROM python:3.6

COPY . /management
WORKDIR /management

RUN pip install -r requirements.txt
RUN pip install -e .

RUN chmod 700 run.sh

