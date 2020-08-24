# Testing the umbox
Something to note is that this test doesn't utilize `main.py`. It relies on the behavior of the packets sent and received between a client and a server with the umbox in the middle.
## Setup
- Create the u1-sniffer-log-stats and set the bandwidth to 5 packets/minute
	- Instructions: https://github.com/SEI-TAS/kalki-umboxes/tree/dev/umboxes
- Open two terminals (inside the tester folder)
	- Terminal 1: 
		- Run `IMAGE=u1-antidos docker-compose up`
	- Terminal 2: 
		- Run `docker exec -it iperf-server sh`
        - Run `apk add iperf3`
    - Terminal 3: 
		- Run `docker exec -it iperf-client sh`
        - Run `apk add iperf3`
    - Terminal 4: 
		- Run `ip route` and get address space of `br_eth1` and `br_eth2` (for simplicity, let br_eth1 address space be 172.30.0.0/16 and let br_eth2 address space be 172.31.0.0/16)
		- Run `sudo ifconfig br_eth2 172.30.0.2/16 up`
	- Terminal 2
		- Run `ip route add 172.31.0.0/16 dev eth0`
	- Terminal 3
		- Run `ip route add 172.30.0.0/16 dev eth0`
	- Terminal 2
		- Run `iperf3 -s 172.30.0.1`
**Note: When running the following commands, if they do not work, first try to ping the server container from the client container and vice versa.**
- Testing the TCP connection limit:
	- In terminal 3, run
    	- `iperf3 -c 172.30.0.2 -P 4`
        - `iperf3 -c 172.30.0.2 -P 5` 
- Testing the bandwidth limit
    - In terminal 3, run `ping 172.30.0.2`

## Intended Behavior/Result
### Testing the TCP connection limit
When running the command with `-P 4`, we should see that the packets are sent successfully from the client container to the server container. However, when running the command with `-P 5`, we should see that the connection refused

Below is a sample output:

/ # iperf3 -c 172.30.0.2 -P 4
Connecting to host 172.30.0.2, port 5201
[  5] local 172.31.0.2 port 34734 connected to 172.30.0.2 port 5201
[  7] local 172.31.0.2 port 34736 connected to 172.30.0.2 port 5201
[  9] local 172.31.0.2 port 34738 connected to 172.30.0.2 port 5201
[ 11] local 172.31.0.2 port 34740 connected to 172.30.0.2 port 5201
[ ID] Interval           Transfer     Bitrate         Retr  Cwnd
[  5]   0.00-1.00   sec   368 KBytes  3.01 Mbits/sec   58   2.83 KBytes       
[  7]   0.00-1.00   sec   368 KBytes  3.01 Mbits/sec   58   2.83 KBytes       
[  9]   0.00-1.00   sec   368 KBytes  3.01 Mbits/sec   58   2.83 KBytes       
[ 11]   0.00-1.00   sec   368 KBytes  3.01 Mbits/sec   58   2.83 KBytes       
[SUM]   0.00-1.00   sec  1.44 MBytes  12.0 Mbits/sec  232    

/ # iperf3 -c 172.30.0.2 -P 5
Connecting to host 172.30.0.2, port 5201
[  5] local 172.31.0.2 port 34744 connected to 172.30.0.2 port 5201
[  7] local 172.31.0.2 port 34746 connected to 172.30.0.2 port 5201
[  9] local 172.31.0.2 port 34748 connected to 172.30.0.2 port 5201
[ 11] local 172.31.0.2 port 34750 connected to 172.30.0.2 port 5201
iperf3: error - unable to connect stream: Connection refused

### Testing the bandwidth limit
You should see that there are five packets send initially, and then one sent every 12 seconds.

Below is a sample output

/ # ping 172.30.0.2
PING 172.30.0.2 (172.30.0.2): 56 data bytes
64 bytes from 172.30.0.2: seq=0 ttl=64 time=0.241 ms
64 bytes from 172.30.0.2: seq=1 ttl=64 time=0.209 ms
64 bytes from 172.30.0.2: seq=2 ttl=64 time=0.211 ms
64 bytes from 172.30.0.2: seq=3 ttl=64 time=0.252 ms
64 bytes from 172.30.0.2: seq=4 ttl=64 time=0.204 ms
64 bytes from 172.30.0.2: seq=12 ttl=64 time=0.209 ms
64 bytes from 172.30.0.2: seq=24 ttl=64 time=0.242 ms
64 bytes from 172.30.0.2: seq=36 ttl=64 time=0.202 ms


