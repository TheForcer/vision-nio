FROM ubuntu:20.04

LABEL name="vision"
LABEL authors="Felix"
LABEL description="General purpose matrix bot based on matrix-nio"

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install libolm-dev python3-minimal python3-pip
ADD requirements.txt /opt/
RUN pip3 install -r /opt/requirements.txt && \
    rm /opt/*

ADD . /opt/
VOLUME ["/opt/config", "/opt/data"]

CMD [ "python3", "/opt/main.py" ]