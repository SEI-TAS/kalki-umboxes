# Testing the umbox
## Setup
- Create the u4-block-all-image
	- Instructions: https://github.com/SEI-TAS/kalki-umboxes/tree/dev/umboxes
- Open three terminals (inside the tester folder)
	- Terminal 1: Run `IMAGE=u4-block-all-image docker-compose up`
	- Terminal 2: Run `sudo main.py` with the necessary configurations
	- Terminal 3: Run `tail -f outgoing.log`
- Send traffic

## Intended Behavior/Result
- From Terminal 3, one should be able to see the traffic sent to the umbox
- From Terminal 2, there should be no packets sent from the umbox