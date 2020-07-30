# Testing the umbox
## Setup
- Create the u10-phillips-brute-force-restrict
	- Instructions: https://github.com/SEI-TAS/kalki-umboxes/tree/dev/umboxes
- Clone the repository https://steveyo.github.io/Hue-Emulator/
- Open four terminals (inside the tester folder)
	- Terminal 1: Run `IMAGE=u10-phillips-brute-force-restrict docker-compose up`
	- Terminal 2: Run `sudo main.py` with the necessary configurations
	- Terminal 3: Run `sudo java -jar HueEmulator-v0.6.jar` and start the program on port 80
	- Terminal 4: Run `sudo python3 -m http.server 8080`
- Go to sniffer/testScripts/phillips_brute_force.sh
	- Change `PHILLIPSIP=10.27.151.106` to `PHILLIPSIP=localhost` 
- Run `bash phillips_brute_force.sh` (ensure PHILLIPSIP of device is set to localhost)
- Go to sniffer/testScripts/phillips_put_test.sh
	- Change curl request to `curl -d '{"hue": 25000}' -X PUT http://localhost:8080/api/newdeveloper/lights/1/state`
- Run `bash phillips_put_test.sh`
 
## Intended Behavior/Result
The following is a snippet from Terminal 1

b'Received: {"alert": "brute-force", "umbox": "4d30ab9097ad", "details": "2020-07-27 17:01:47 WARNING  BRUTE_FORCE: IP address 127.0.0.1 has attempted device api calls with 5 different tokens within 10 seconds\\n"}'
umbox           | Umbox id: 4d30ab9097ad
umbox           | Sending alert brute-force
umbox           | http://alert-server:6060/alert/
umbox           | -----------START-----------
umbox           | POST http://alert-server:6060/alert/
umbox           | Content-Type: application/json
umbox           | Content-Length: 94
umbox           | 
umbox           | b'{"alert": "brute-force", "umbox": "4d30ab9097ad", "details": "ALERT: BRUTE_FORCE detected!\\n"}'
umbox           | <Response [200]>
umbox           | b'Received: {"alert": "brute-force", "umbox": "4d30ab9097ad", "details": "ALERT: BRUTE_FORCE detected!\\n"}'
umbox           | restricted API request method: PUT