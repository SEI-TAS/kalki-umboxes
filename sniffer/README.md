# Sniffer
* [Overview](#overview)
* [Setup](#setup)
* [Packet Handlers](#packet-handlers)
	* [Max Login and Default Login](#max-login-and-default-login)
	* [Phillips Hue Brute Force](#phillips-hue-brute-force)
	* [Udoo Neo Brute Force](#udoo-neo-brute-force)
	* [HTTP Authentication "Firewall"](#http-basic-authentication-"firewall")
* [Networking](#networking)
	* [TCP Connection Hijacking](#tcp-connection-hijacking)
* [Configuration](#configuration)
* [Test Scripts](#test-scripts)


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

### Max login and default login
This handler checks if the given TCP packet has HTTP data and if so, parses it into an HTTP packet.  It checks to see if the HTTP request is using Basic HTTP Authentication.  If so, it looks for two things.  First, it checks if the request is using the default username and password for authentication.  If it is, it will write an alert message to the log file to be read by the alerter.  No matter the username or password, this handler will keep track of consecutive  authentication attempts and if enough attempts are made within a time interval configured in the configuration file, it will also write an alert to the log file to be read by the alerter.

### Phillips Hue Brute Force
This handler checks if the given TCP packet has HTTP data and if so, parses it into an HTTP packet.  Its purpose is to detect brute force attacks on the phillips hue API.  It does this by checking the path of the HTTP request.  It looks for two types of paths.  The first is any request to the path __/api__.  Any user sending this request is attempting to retrieve an API token for the device.  If they obtained this, they would have full control over the device.  If the handler detects a number of these requests within a configured time interval, it will write an alert to the log to be read by the alerter.  Secondly, this handler is observing requests with the path __/api/[token]/*__ where [token] could be any sequence of numbers and letters and * could be any remainder to the path.  The handler will look for requests with this path pattern from the same IP that use different tokens.  Once a configured amount of these requests occur within a configured amount of time, an alert will be appended to the log.  This represents a malicious user attempting to find a valid token so that they may communicate with the device. 

### Udoo Neo Brute Force
This handler checks all TCP packets to search for the start of the TCP handshake.  Its purpose is to identify an SSH brute force attempt by observing many new TCP connections from the same IP address.  A new TCP connection is qualified as any TCP packet sent with just the SYN flag set.  If the handler sees a configured number of new connections from the same source IP within a configured time interval, it will write an alert to the log file.  

### HTTP Basic Authentication "Firewall"
The purpose of this handler is to add an authentication layer using HTTP basic authentication to devices that do not already have authentication.  It does this by checking all incoming packets for the HTTP basic authentication header.  For all HTTP requests that do not have this header it will send back a 401 unauthorized response as if it were the device and the actual device will never recieve the request.  For all HTTP requests that do have the authentication header, but were not able to authenticate based on the stored password file, the handler will do the same.  In the case that the handler recieves an HTTP request that it is able to authenticate based on the password file, it will forward the request to the device as normal.  Passwords can be saved by running the script `python3 testScripts/savePassword.py`.  This script stores an md5 hash of the given password, for some level of security, that will be used to authenticate requests.  This handler makes heavy use of the __hijackTCP__ library described in __networking__ section.  It needs to utilize this in order to send a response back to the client on the same TCP connection that was made with the device.

## Networking

### TCP Connection Hijacking
In the file __hijackTCP.py__ is functionality to hijack a TCP connection between a user and a device.  The purpose of this is to be able to send responses back to the user as if they were coming from the device.  This library constructs the appropriate TCP and IP headers and sends on an IP socket in order to not handle the ethernet layer.  This library consists of four functions to be used by a handler.  Because TCP is designed to be extremely fault tolerant, this library is carefully designed to properly terminate connections on both the client and device side so that stale tcp connections do not timeout, but instead terminate as a result of us hijacking the connection.

#### sendResponse(response, ip_packet, tcp_packet)
Given a response to send from the handler and the incoming parsed ip and tcp packets from the user, send a response back to the client as if it were coming from the device with the correct headers.

#### sendDeviceTeardown(ip_packet, tcp_packet)
Given the original parsed ip and tcp packets from the user, send a tcp connection teardown to the device as if it were coming from the user.  This is to avoid the device keeping a stale connection open that will simply time out because the handler has intercepted all packets.  This function should be invoked by a handler directly after it has sent a response back to the user.

#### respondDeviceTeardown(ip_packet, tcp_packet) 
Given the parsed ip and tcp packets from the device in response to the teardown request sent, send a final acknowledgment to the device to complete the tcp connection teardown.  It is up to the handler to do the proper checks to find the FIN, ACK response from the device and call this function when it recieves that message.

#### respondClientTeardown(ip_packet, tcp_packet)
Once a response is sent back to the client's request, the client will initiate a tcp teardown.  It is the handler's responsibility to identify this teardown message and invoke this function with the parsed ip and tcp packets from that message.  This function will send a proper response back to the client in order to complete the tcp teardown process

## Configuration
The sniffer is configured through the configuration file *config.json*.  
* specify network interface to retrieve incoming traffic from as a string in property "incomingNIC"
* specify network interface to send outgoing traffic to as a string in property "outgoingNIC"
* specify which handler should be used in property "handler" out of options:
	* "maxLogin"
	* "httpAuth"
	* "phillipsHue"
	* "udooNeo"
* specify if packets should be forwarded to their destination by specifying "on" for the property "echo"
* specify a list of restricted IPv4 addresses as strings of dotted quads
* specific configurations for each handler

## Test Scripts
In the testScripts folder can be found scripts to:
* run a simple HTTP server
* send an HTTP request to the server with Basic HTTP Authentication using a default username and password
* Send an HTTP request using to `/api/[token]/lights` where token is a random 16 character UUID
* Simulate a phillips hue brute force API attack by sending multiple successive requests with different tokens
* Simulate an SSH brute force attack by trying to ssh a specified number of times with random passwords of length 16
* Store a hashed username and password relationship for use by the httpAuthHandler
