# Umbox Tester

This is a program that will allow for easy testing of the umboxes.

## Setup/Configuration 
The following should be set up on the computer:
- Python3
- Python modules
	- requests
- docker-compose (needs to support version 3.5)

## Running Tester

To run:
- `IMAGE={umbox image name} docker-compose up`
- `sudo python3 main.py --time <time (int)> --udp --interface <interface> --parser <number (int)>`
	- time (DEFAULT=3): The waiting time (seconds) before discarding a sent packet 
	- udp: by default the tester will send only TCP/IP packets. To send only UDP packets, specify it with the `--udp` flag
	- interface (DEFAULT=lo): The interface to listen to. Packets sent by this interface are forwarded to eth1.
	- parser (DEFAULT=0): The number of the function used to parse the packets sent through eth1 to compare to packets received from eth2

After running:
- `docker-compose down`

## umbox Testing Notes
Currently, the following umboxes have not been tested yet with this tester:
- u2-http-auth-proxy
- u3-http-auth-proxy-block
- u-12-snort-block-xmas

For the rest of the umboxes, there is a README inside the umbox's docker image folder describing how to test it.
