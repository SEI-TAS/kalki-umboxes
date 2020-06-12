FROM python:3.5-alpine

RUN apk --no-cache add bash iproute2 nano

# Setup Alerter.
COPY ./alerter /alerter
WORKDIR /alerter
RUN ["bash", "alerter_setup.sh"]
WORKDIR /
