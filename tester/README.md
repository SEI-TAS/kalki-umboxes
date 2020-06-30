# Umbox Tester

This is a program that will allow for easy testing of the umboxes.

To run:
- `IMAGE={umbox image name} docker-compose up`
- `sudo python3 main.py --ip <ipaddress> --port <port> --time <time>`
	- ip (str): The ip address to get the traffic from
	- port (int): The port number to connect with the ip address
	- time (int): The waiting time before discarding a sent packet 

After running:
- `docker-compose down`
