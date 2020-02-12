# Umboxes

## Overview

This folder contains a series of configurations and scripts used to create either VM-based or container-based umboxes.
All the folders inside "standard" contain configurations for specific umboxes. The rest of the folders inside the "common"
folder have supporting common configs or scripts to help in creating them. More specifically:

- alerter_docker: has a script and Docker config to create an alerter container.
- alerter_vm_base: has scripts and configurations for the alerter to go inside a VM-based umbox.
- sniffer_docker: has a script and Docker config to create an sniffer container, as well as common things for container
umboxes based on the sniffer.
- sniffer_vm_base: has scripts and configurations for the sniffer to go inside a VM-based umbox.
- snort_base: common configs for a snort-based umbox.

## Setup
The sniffer is implemented in Python 3 and run using pipenv as a virtual environment.

1. Install Python 3 and pip3.
    1. If running in Ubuntu, execute `bash alerter_deps_setup.sh` for the appropriate debian packages to be installed.
1. Install pipenv and set up the Python environment with the needed dependencies:
    1. Execute `bash alerter_setup.sh`

## Configuration
Configure the sniffer by changing `config.json` as needed.

Parameters that can be configured are:

- **control_node_ip**: the IP address of the control node. Alerts will be sent to this address.
- **log_file**: full path and filename of the log file the Alerter will be monitoring.
- **id_source**: where to get the ID of this umbox from, to send as the id of the sender when sending an alert. The only
valid values are "mac" and "hostname"
- **patterns**: a set of patterns to find inside the configured logfile. Each pattern is a map with two key-value pairs:
    - **search_text**: the specific string to look for inside the logfile.
    - **alert_text**: the alert type name to send to the Control node when the search_text string is found.

## Execution
1. Run the alerter by executing `sudo bash alerter.sh`

