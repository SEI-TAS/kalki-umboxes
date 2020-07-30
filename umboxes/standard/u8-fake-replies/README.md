# Testing the umbox
## Setup
- Create the u8-fake-replies
	- Instructions: https://github.com/SEI-TAS/kalki-umboxes/tree/dev/umboxes
- Clone the repository https://github.com/iancmcc/ouimeaux 
- Open two terminals (inside the tester folder)
	- Terminal 1: Run `IMAGE=u8-fake-replies docker-compose up`
	- Terminal 2: Run `sudo main.py` with the necessary configurations
- Run `python3 client.py --device localhost --on` (from ouimeaux folder)
 
## Intended Behavior/Result
#### The following is a snippet from Terminal 1

umbox           | Received HTTP request: 
umbox           | Method: POST
umbox           | URI: /upnp/control/basicevent1
umbox           | Version: HTTP/1.1
umbox           | Host: localhost:49153
umbox           | Authorization: None
umbox           | 
umbox           | Sending response message!
umbox           | Sending response message!
umbox           | Sending response message!
umbox           | Sending response message!

#### The following is from terminal 2
ETH3 b'\x02B\xac\x1d\x00\x02\x00\x00\x00\x00\x00\x00\x08\x00E\x00\x00(\xd41\x00\x00@\x06\xa8\x9c\x7f\x00\x00\x01\x7f\x00\x00\x01\xc0\x01\xc8$\xdc\xe6\x18\xbf\xf8o\xda*P\x10\x08\x00Yk\x00\x00'
ETH3 b'\x02B\xac\x1d\x00\x02\x00\x00\x00\x00\x00\x00\x08\x00E\x00\x00\xe8\xd41\x00\x00@\x06\xa7\xdc\x7f\x00\x00\x01\x7f\x00\x00\x01\xc0\x01\xc8$\xdc\xe6\x18\xbf\xf8o\xda*P\x10\x08\x00g\x8e\x00\x00HTTP/1.1 200 OK\r\nCONTENT-LENGTH: 435\r\nCONTENT-TYPE: text/xml; charset="utf-8"\r\nDATE: Wed, 04 Dec 2019 20:57:23 GMT\r\nEXT:\r\nSERVER: Unspecified, UPnP/1.0, Unspecified\r\nX-User-Agent: redsonic\r\n\r\n'
ETH3 b'\x02B\xac\x1d\x00\x02\x00\x00\x00\x00\x00\x00\x08\x00E\x00\x01\xdb\xd41\x00\x00@\x06\xa6\xe9\x7f\x00\x00\x01\x7f\x00\x00\x01\xc0\x01\xc8$\xdc\xe6\x19\x7f\xf8o\xda*P\x10\x08\x00\xc4S\x00\x00<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>\n<u:SetBinaryStateResponse xmlns:u="urn:Belkin:service:basicevent:1">\r\n<BinaryState>0|1575492954|89|8483|94128|1209600|18|18120|2334843|26129393</BinaryState>\r\n<CountdownEndTime>0</CountdownEndTime>\r\n<deviceCurrentTime>1575493043</deviceCurrentTime>\r\n</u:SetBinaryStateResponse>\r\n</s:Body> </s:Envelope>'