FROM python:3.5-alpine

RUN apk --no-cache add bash iproute2 nano
RUN pip3 install pipenv==2018.11.26

# Setup Alerter.
COPY ./alerter /alerter
WORKDIR /alerter

# Used to wait for required eth interfaces
COPY ./umboxes/common/alerter_docker/wait_on_ifaces.sh /wait_on_ifaces.sh

# Install packages, temporarily installing GCC and deps.
RUN apk --no-cache add build-base linux-headers && \
    pipenv install --system --deploy --ignore-pipfile && \
    apk del build-base linux-headers

WORKDIR /
