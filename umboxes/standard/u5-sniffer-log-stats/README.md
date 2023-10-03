# Testing the umbox
## Setup
- Create the u5-sniffer-log-stats
	- Instructions: https://github.com/SEI-TAS/kalki-umboxes/tree/dev/umboxes
- Open two terminals (inside the tester folder)
	- Terminal 1: Run `IMAGE=u5-sniffer-log-stats docker-compose up`
	- Terminal 2: Run `sudo main.py` with the necessary configurations
- Send traffic

## Intended Behavior/Result
One should be able to observe alerts sent from the umbox logging information.

The following is a snippet from Terminal 1

umbox           | 2020-07-21 06:21:34 WARNING  LOG_INFO: Packet stats total: 12 tcp: 10 udp: 2 other: 0
umbox           | 2020-07-21 06:21:34 WARNING  LOG_INFO: Packets sent from 192.168.0.193 stats total: 12 tcp: 10 udp: 2 other: 0
umbox           | 2020-07-21 06:21:34 WARNING  LOG_INFO: Packets sent from 172.29.0.1 stats total: 12 tcp: 10 udp: 2 other: 0
umbox           | 2020-07-21 06:21:34 WARNING  LOG_INFO: Packets sent to 35.186.224.47 stats total: 12 tcp: 10 udp: 2 other: 0
umbox           | 2020-07-21 06:21:34 WARNING  LOG_INFO: Packets sent to 172.29.255.255 stats total: 12 tcp: 10 udp: 2 other: 0
umbox           | 2020-07-21 06:21:34 WARNING  LOG_INFO: Packets sent to 172.253.122.139 stats total: 12 tcp: 10 udp: 2 other: 0
umbox           | 2020-07-21 06:21:34 WARNING  LOG_INFO: Packets sent to 35.190.244.124 stats total: 12 tcp: 10 udp: 2 other: 0