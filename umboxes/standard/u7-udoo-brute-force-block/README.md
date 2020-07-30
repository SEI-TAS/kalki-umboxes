# Testing the umbox
## Setup
- Create the u7-udoo-brute-force-block
	- Instructions: https://github.com/SEI-TAS/kalki-umboxes/tree/dev/umboxes
- Open three terminals (inside the tester folder)
	- Terminal 1: Run `IMAGE=u7-udoo-brute-force-block docker-compose up`
	- Terminal 2: Run `sudo main.py` with the necessary configurations
	- Terminal 3: Run `sudo python3 -m http.server 22`
- Go to sniffer/testScripts/udoo_neo_brute_force.py
	- Change `UDOOIP=10.27.151.101` to `UDOOIP=localhost` 
- Run `python3 udoo_neo_brute_force.py` (from sniffer/testScripts)

## Intended Behavior/Result
The following are snippets from Terminal 1

umbox           | 2020-07-30 15:23:25 WARNING  COMPROMISE: Detected 2 invalid UDP packets and + 3 invalid TCP packets from device at 127.0.0.1, exceeding limit of 5
umbox           | ALERT: COMPROMISE detected!
umbox           | Email Sent!
umbox           | No valid email server connection.  Email not sent.
umbox           | COMPROMISE attempt detected from 127.0.0.1; adding to restricted list
umbox           | 2020-07-30 15:23:25 WARNING  BRUTE_FORCE: IP address 127.0.0.1 has started 5 TCP connections within 10 seconds
umbox           | ALERT: BRUTE_FORCE detected!


**Note: Running `udoo_neo_brute_force.py` again does not invoke a response from the umbox**