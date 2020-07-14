# Umbox Tester

This is a program that will allow for easy testing of the umboxes.

## Setup/Configuration 
The following should be set up on the computer:
- Python3
- Python modules
	- scapy 2.0
	- requests
- docker-compose (needs to support version 3.5)

## Running Tester

To run:
- `IMAGE={umbox image name} docker-compose up`
- `sudo python3 main.py --time <time> --udp`
	- time (int): The waiting time (seconds) before discarding a sent packet 
	- udp: by default the tester will send only TCP/IP packets. To send only UDP packets, specify it with the `--udp` flag

After running:
- `docker-compose down`
