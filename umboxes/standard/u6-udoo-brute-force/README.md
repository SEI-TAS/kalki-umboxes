# Testing the umbox
## Setup
- Create the u6-udoo-brute-force
	- Instructions: https://github.com/SEI-TAS/kalki-umboxes/tree/dev/umboxes
- Open three terminals (inside the tester folder)
	- Terminal 1: Run `IMAGE=u6-udoo-brute-force docker-compose up`
	- Terminal 2: Run `sudo main.py` with the necessary configurations
	- Terminal 3: Run `sudo python3 -m http.server 22`
- Go to sniffer/testScripts/udoo_neo_brute_force.py
	- Change `UDOOIP=10.27.151.101` to `UDOOIP=localhost` 
- Run `python3 udoo_neo_brute_force.py` (from sniffer/testScripts)

## Intended Behavior/Result
The following is a snippet from Terminal 1

umbox           | 2020-07-22 16:44:37 WARNING  COMPROMISE: Detected 2 invalid UDP packets and + 3 invalid TCP packets from device at 127.0.0.1, exceeding limit of 5
umbox           | ALERT: COMPROMISE detected!
umbox           | 2020-07-22 16:44:37 WARNING  BRUTE_FORCE: IP address 127.0.0.1 has started 5 TCP connections within 10 seconds
umbox           | ALERT: BRUTE_FORCE detected!