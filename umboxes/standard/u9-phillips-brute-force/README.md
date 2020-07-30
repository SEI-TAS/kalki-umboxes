# Testing the umbox
## Setup
- Create the u9-phillips-brute-force
	- Instructions: https://github.com/SEI-TAS/kalki-umboxes/tree/dev/umboxes
- Clone the repository https://steveyo.github.io/Hue-Emulator/
- Open three terminals (inside the tester folder)
	- Terminal 1: Run `IMAGE=u9-phillips-brute-force docker-compose up`
	- Terminal 2: Run `sudo main.py` with the necessary configurations
	- Terminal 3: Run `sudo java -jar HueEmulator-v0.6.jar` and start the program on port 80
- Go to sniffer/testScripts/phillips_brute_force.sh
	- Change `PHILLIPSIP=10.27.151.106` to `PHILLIPSIP=localhost` 
- Run `bash phillips_brute_force.sh` (from sniffer/testScripts)
 
## Intended Behavior/Result
We should be able to see a brute-force alert with information regarding who and how the brute-force was triggered

The following is a snippet from Terminal 1

b'{"alert": "brute-force", "details": "2020-07-22 14:57:19 WARNING  BRUTE_FORCE: IP address 127.0.0.1 has attempted device api calls with 5 different tokens within 10 seconds\\n", "umbox": "ba33a9022bf7"}'