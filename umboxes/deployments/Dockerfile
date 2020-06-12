ARG UMBOX_IMAGE
FROM $UMBOX_IMAGE

# Setup deployment-specific config for this umbox.
ARG DEPLOYMENT
COPY $DEPLOYMENT/config_alerter.json /sniffer/config.json
