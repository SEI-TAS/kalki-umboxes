# Sniffer
* [Overview] (#overview)
* [Setup] (#setup)
* [Packet Handlers] (#packet-handlers)
	* [HTTP Basic Authentication] (#httpauthhandler.py)
	* [Phillips Hue] (#phillipsHueHandler.py)
* [Configuration] (#configuration)
* [Test Scripts] (#test-scripts)


## Overview

The contents of this directory make up the packet sniffer.  It reads every packet
entering and leaving the Ubuntu network stack using a raw socket in Python.  The sniffer first starts by parsing the raw data from the socket as an Ethernet packet.  It checks the ethernet protocol to ensure that it is IPv4 and ignores the packet otherwise.  It then parses the ethernet data as and IPv4 packet.  If the IP packet is not using TCP it will ignore it.  If it is using TCP, it will parse the IP data as a TCP packet.  It then passes the TCP and IPv4 packet to a packet handler that is configured using the config file.  The packet handler is the important part as it will be used to identify basic HTTP authentication and brute force attacks, and also restrict packets from specific host IP addresses.

## Setup
The sniffer is implemented in Python 3.6 and run using pipenv as a virtual environment
Since the sniffer utilizes Python raw sockets, it must be run as a root user and is only runnable on a linux based machine.
1. Install Python 3.6 by running `sudo apt-get install python3` 
2. Ensure `pip` is installed on your machine by running `pip --version`
3. Install `pipenv` as the root user by running `sudo -H python3 -m pip install pipenv`
	* this specific command gets around an issue with the pip wrapper by running the module directly with python
4. install all environement dependencies specified in the pipfile by running `pipenv install` 
5. Configure the sniffer by changing config.json
6. run the sniffer by running `sudo ./sniffer.sh`

## Packet Handlers

### httpAuthHandler.py
This handler checks if the given TCP packet has HTTP data and if so, parses it into an HTTP packet.  It checks to see if the HTTP request is using Basic HTTP Authentication.  If so, it looks for two things.  First, it checks if the request is using the default username and password for authentication.  If it is, it will write an alert message to the log file to be read by the alerter.  No matter the username or password, this handler will keep track of consecutive  authentication attempts and if enough attempts are made within a time interval configured in the configuration file, it will also write an alert to the log file to be read by the alerter.

### phillipsHueHandler.py
This handler checks if the given TCP packet has HTTP data and if so, parses it into an HTTP packet.  Its purpose is to detect brute force attacks on the phillips hue API.  It does this by checking the path of the HTTP request.  It looks for two types of paths.  The first is any request to the path __/api__.  Any user sending this request is attempting to retrieve an API token for the device.  If they obtained this, they would have full control over the device.  If the handler detects a number of these requests within a configured time interval, it will write an alert to the log to be read by the alerter.  Secondly, this handler is observing requests with the path __/api/[token]/*__ where [token] could be any sequence of numbers and letters and * could be any remainder to the path.  The handler will look for requests with this path pattern from the same IP that use different tokens.  Once a configured amount of these requests occur within a configured amount of time, an alert will be appended to the log.  This represents a malicious user attempting to find a valid token so that they may communicate with the device. 

## Configuration
The sniffer is configured through the configuration file *config.json*.  
* specify network interface to retrieve traffic from as a string in property "nic"
* specify which handler should be used in property "handler" 3out of options:
	* "httpAuth"
	* "phillipsHue"
* specific configurations for each handler

## Test Scripts
In the testScripts folder can be found scripts to:
* run a simple HTTP server
* send an HTTP request to the server with Basic HTTP Authentication using a default username and password
* Send an HTTP request using to `/api/[token]/lights` where token is a random 16 character UUID
* Simulate a phillips hue brute force API attack by sending multiple successive requests with different tokens
