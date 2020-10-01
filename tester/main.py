# 
#  Kalki - A Software-Defined IoT Security Platform
#  Copyright 2020 Carnegie Mellon University.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
#  [DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
#  This Software includes and/or makes use of the following Third-Party Software subject to its own license:
#  1. Google Guava (https://github.com/google/guava) Copyright 2007 The Guava Authors.
#  2. JSON.simple (https://code.google.com/archive/p/json-simple/) Copyright 2006-2009 Yidong Fang, Chris Nokleberg.
#  3. JUnit (https://junit.org/junit5/docs/5.0.1/api/overview-summary.html) Copyright 2020 The JUnit Team.
#  4. Play Framework (https://www.playframework.com/) Copyright 2020 Lightbend Inc..
#  5. PostgreSQL (https://opensource.org/licenses/postgresql) Copyright 1996-2020 The PostgreSQL Global Development Group.
#  6. Jackson (https://github.com/FasterXML/jackson-core) Copyright 2013 FasterXML.
#  7. JSON (https://www.json.org/license.html) Copyright 2002 JSON.org.
#  8. Apache Commons (https://commons.apache.org/) Copyright 2004 The Apache Software Foundation.
#  9. RuleBook (https://github.com/deliveredtechnologies/rulebook/blob/develop/LICENSE.txt) Copyright 2020 Delivered Technologies.
#  10. SLF4J (http://www.slf4j.org/license.html) Copyright 2004-2017 QOS.ch.
#  11. Eclipse Jetty (https://www.eclipse.org/jetty/licenses.html) Copyright 1995-2020 Mort Bay Consulting Pty Ltd and others..
#  12. Mockito (https://github.com/mockito/mockito/wiki/License) Copyright 2007 Mockito contributors.
#  13. SubEtha SMTP (https://github.com/voodoodyne/subethasmtp) Copyright 2006-2007 SubEthaMail.org.
#  14. JSch - Java Secure Channel (http://www.jcraft.com/jsch/) Copyright 2002-2015 Atsuhiko Yamanaka, JCraft,Inc. .
#  15. ouimeaux (https://github.com/iancmcc/ouimeaux) Copyright 2014 Ian McCracken.
#  16. Flask (https://github.com/pallets/flask) Copyright 2010 Pallets.
#  17. Flask-RESTful (https://github.com/flask-restful/flask-restful) Copyright 2013 Twilio, Inc..
#  18. libvirt-python (https://github.com/libvirt/libvirt-python) Copyright 2016 RedHat, Fedora project.
#  19. Requests: HTTP for Humans (https://github.com/psf/requests) Copyright 2019 Kenneth Reitz.
#  20. netifaces (https://github.com/al45tair/netifaces) Copyright 2007-2018 Alastair Houghton.
#  21. ipaddress (https://github.com/phihag/ipaddress) Copyright 2001-2014 Python Software Foundation.
#  DM20-0543
#
#

import sys
from threading import Thread
from helper import *
from threadFunctions import *
import argparse

ETH_P_ALL = 3
eth1_bridge_name = "br_eth1"
veths = getVeth()
eth2_veth = veths[0]
eth3_veth = veths[1]

def main(timeout, interface, udp, parser):

	eth1Socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
	eth1Socket.bind((eth1_bridge_name, 0))

	eth2Socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
	eth2Socket.bind((eth2_veth, 0))

	eth3Socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
	eth3Socket.bind((eth3_veth, 0))
	
	t1 = Thread(target=startSender, args=[eth1Socket, interface, udp])
	t2 = Thread(target=startReceiverETH2, args=[eth2Socket])
	t3 = Thread(target=startReceiverETH3, args=[eth3Socket])
	t4 = Thread(target=startQueueProcessor, args=[timeout, parser])
	t5 = Thread(target=startAlertProcesser)

	t1.start()
	t2.start()
	t3.start()
	t4.start()
	t5.start()


if(__name__=="__main__"):
	parser = argparse.ArgumentParser()
	parser.add_argument("--time", type=int, help="enter time to wait for checker",
                    nargs='?', default=3)
	parser.add_argument("--interface", type=str, help="enter interface",
                    nargs='?', default="lo")
	parser.add_argument("--parser", type=int, help="enter parsing function number",
                    nargs='?', default=0)
	parser.add_argument("--udp", action="store_true")
	
	args = vars(parser.parse_args())
	main(args["time"], args["interface"], args["udp"], args["parser"])