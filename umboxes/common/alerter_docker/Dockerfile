FROM python:3.5-alpine

# Setup Alerter.
COPY ./alerter /alerter
WORKDIR /alerter
RUN ["bash", "alerter_setup.sh"]
WORKDIR /
