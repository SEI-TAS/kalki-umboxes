# Kalki Umboxes

This repository has several components that are needed for building umbox. In particular:

- **alerter**: Python-based module that looks for alerts in logfiles inside an umbox, and send alerts to the Control node.
- **sniffer**: Python-based packet analyzer software that has several sample functionalities that can be used to showcase
things that umboxes can do.
- **umboxes**: specific and common configuration files to create either VM or container based umboxes.

Please see the readmes in each subfolder for more details.

Kalki is an IoT platform for allowing untrusted IoT devices to connect to a network in a secure way, protecting both the IoT device and the network from malicious attackers.

Kalki comprises a total of 8 GitHub projects:
- kalki-node-setup (Kalki Main Repository, composes all non-UI components)
- kalki-controller (Kalki Main Controller)
- kalki-umbox-controller (Kalki Umbox Controller)
- kalki-device-controller (Kalki Device Controller)
- kalki-dashboard (Kalki Dashboard)
- kalki-db (Kalki Database Library)
- kalki-iot-interface (Kalki IoT Interface)
- kalki-umboxes (Kalki Umboxes, sample umboxes and umboxes components)
