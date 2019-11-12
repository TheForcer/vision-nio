FROM python:3.8-alpine

LABEL name="vision"
LABEL authors="Felix"
LABEL description="General purpose matrix bot based on matrix-nio"

ADD . /opt/
VOLUME ["/opt/config", "/opt/data"]

RUN apk add --no-cache --virtual alpine-sdk autoconf automake libtool gcc g++ make libffi-dev openssl-dev && \
    pip install -r /opt/requirements.txt && \
    apk del alpine-sdk autoconf automake libtool gcc g++ make libffi-dev openssl-dev

CMD [ "python3", "/opt/main.py" ]