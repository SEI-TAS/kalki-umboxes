# Sniffer
* [Overview](#overview)
* [Setup](#setup)
* [Packet Handlers](#packet-handlers)
	* [HTTP Basic Authentication](#http-basic-authentication)
	* [Phillips Hue Brute Force](#phillips-hue-brute-force)
	* [Udoo Neo Brute Force](#udoo-neo-brute-force)
* [Configuration](#configuration)
* [Test Scripts](#test-scripts)


## Overview

The contents of this directory make up the packet sniffer.  It reads every packet
entering and leaving the Ubuntu network stack using a raw socket in Python.  The sniffer first starts by parsing the raw data from the socket as an Ethernet packet.  It checks the ethernet protocol to ensure that it is IPv4 and ignores the packet otherwise.  It then parses the ethernet data as and IPv4 packet.  If the IP packet is not using TCP it will ignore it.  If it is using TCP, it will parse the IP data as a TCP packet.  It then passes the TCP and IPv4 packet to a packet handler that is configured using the config file.  The packet handler is the important part as it will be used to identify basic HTTP authentication and brute force attacks, and also restrict packets from specific host IP addresses.

## Setup
The sniffer is implemented in Python 3.5 and run using pipenv as a virtual environment.
Since the sniffer utilizes Python raw sockets, it must be run as a root user and is only runnable on a linux based machine.

1. Install Python 3 and pip3.
    1. If running in Ubuntu, execute `bash sniffer_deps_setup.sh` for the appropriate debian packages to be installed.
1. Install pipenv and set up the Python environment with the needed dependencies:
    1. Execute `sudo -H bash sniffer_setup.sh`
1. Configure the sniffer by changing `config.json` as needed.
1. Run the sniffer by executing `sudo bash sniffer.sh`

## Packet Handlers

### HTTP Basic Authentication
This handler checks if the given TCP packet has HTTP data and if so, parses it into an HTTP packet.  It checks to see if the HTTP request is using Basic HTTP Authentication.  If so, it looks for two things.  First, it checks if the request is using the default username and password for authentication.  If it is, it will write an alert message to the log file to be read by the alerter.  No matter the username or password, this handler will keep track of consecutive  authentication attempts and if enough attempts are made within a time interval configured in the configuration file, it will also write an alert to the log file to be read by the alerter.

### Phillips Hue Brute Force
This handler checks if the given TCP packet has HTTP data and if so, parses it into an HTTP packet.  Its purpose is to detect brute force attacks on the phillips hue API.  It does this by checking the path of the HTTP request.  It looks for two types of paths.  The first is any request to the path __/api__.  Any user sending this request is attempting to retrieve an API token for the device.  If they obtained this, they would have full control over the device.  If the handler detects a number of these requests within a configured time interval, it will write an alert to the log to be read by the alerter.  Secondly, this handler is observing requests with the path __/api/[token]/*__ where [token] could be any sequence of numbers and letters and * could be any remainder to the path.  The handler will look for requests with this path pattern from the same IP that use different tokens.  Once a configured amount of these requests occur within a configured amount of time, an alert will be appended to the log.  This represents a malicious user attempting to find a valid token so that they may communicate with the device. 

### Udoo Neo Brute Force
This handler checks all TCP packets to search for the start of the TCP handshake.  Its purpose is to identify an SSH brute force attempt by observing many new TCP connections from the same IP address.  A new TCP connection is qualified as any TCP packet sent with just the SYN flag set.  If the handler sees a configured number of new connections from the same source IP within a configured time interval, it will write an alert to the log file.  

## Configuration
The sniffer is configured through the configuration file *config.json*.  
* specify network interface to retrieve traffic from as a string in property "nic"
* specify which handler should be used in property "handler" out of options:
	* "httpAuth"
	* "phillipsHue"
	* "udooNeo"
* specific configurations for each handler

## Test Scripts
In the testScripts folder can be found scripts to:
* Run a simple HTTP server
* Send an HTTP request to the server with Basic HTTP Authentication using a default username and password
* Send an HTTP request using to `/api/[token]/lights` where token is a random 16 character UUID
* Simulate a phillips hue brute force API attack by sending multiple successive requests with different tokens
* Simulate an SSH brute force attack by trying to ssh a specified number of times with random passwords of length 16
