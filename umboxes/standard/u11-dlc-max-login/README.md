# Testing the umbox
Note: This umbox tests max-logins on digest authentication on the dlink camera. The following tests the max-login alert on a digest authentication

## Setup
- Create the u11-dlc-max-login
	- Instructions: https://github.com/SEI-TAS/kalki-umboxes/tree/dev/umboxes
- Open three terminals (inside the tester folder)
	- Terminal 1: Run `IMAGE=u11-dlc-max-login docker-compose up`
	- Terminal 2: Run `sudo main.py` with the necessary configurations
- On Terminal 3, run `curl --ipv4 --user guest:guest --digest http://httpbin.org/digest-auth/auth/user/passwd` repeatedly

## Intended Behavior/Result
An alert stating "max-login-attempts" should be sent with additional details regarding the event.

The following is a snippet from Terminal 1

2020-07-27 13:14:25 WARNING  MULTIPLE_LOGIN : More than 5 attempts in 0.9173427184422811 minutes from same IP address
umbox           | MULTIPLE_LOGIN : More than 5 attempts in 0.9173427184422811 minutes from same IP address
umbox           | ALERT: MULTIPLE_LOGIN detected!
umbox           | Umbox id: 010f2b90e3f7
umbox           | Sending alert max-login-attempts
umbox           | http://alert-server:6060/alert/
umbox           | -----------START-----------
umbox           | POST http://alert-server:6060/alert/
umbox           | Content-Type: application/json
umbox           | Content-Length: 190
umbox           | 
umbox           | b'{"umbox": "010f2b90e3f7", "alert": "max-login-attempts", "details": "2020-07-27 13:14:25 WARNING  MULTIPLE_LOGIN : More than 5 attempts in 0.9173427184422811 minutes from same IP address\\n"}'
umbox           | <Response [200]>
umbox           | b'Received: {"umbox": "010f2b90e3f7", "alert": "max-login-attempts", "details": "2020-07-27 13:14:25 WARNING  MULTIPLE_LOGIN : More than 5 attempts in 0.9173427184422811 minutes from same IP address\\n"}'