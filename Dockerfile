FROM ubuntu:19.10

LABEL name="vision"
LABEL authors="Felix"
LABEL description="General purpose matrix bot based on matrix-nio"

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install libolm-dev python3 python3-pip python3-setuptools
ADD requirements.txt /opt/
RUN pip3 install -r /opt/requirements.txt && \
    rm /opt/*

ADD . /opt/
VOLUME ["/opt/config", "/opt/data"]

CMD [ "python3", "/opt/main.py" ]