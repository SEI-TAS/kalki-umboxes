#!/bin/bash

if [[ -z "$USERNAME" ]]; then
    USERNAME="tommy"
fi

if [[ -z "$PASSWORD" ]]; then
    PASSWORD="iotsec"
fi

sudo htpasswd -b -c /etc/squid/passwords $USERNAME $PASSWORD
sudo chmod o+r /etc/squid/passwords

sudo squid -NYCd 1
