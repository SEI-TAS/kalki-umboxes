#!/bin/bash

DAQ_VERSION=2.0.6 
SNORT_VERSION=2.9.14.1 

sudo apt-get update
sudo apt-get install -yqq build-essential \
	wget \
	tar \
	bison \
	flex \
	libdumbnet-dev \
	liblzma-dev \
	libpcap-dev \
	libpcre3-dev \
	libssl-dev \
	openssl \
	zlib1g-dev \
	libnghttp2-dev \
	libluajit-5.1-dev

wget https://www.snort.org/downloads/snort/daq-${DAQ_VERSION}.tar.gz \
	&& tar xvfz daq-${DAQ_VERSION}.tar.gz \
	&& cd daq-${DAQ_VERSION} \
	&& ./configure \
	&& make \
	&& sudo make install && cd ..

wget https://www.snort.org/downloads/snort/snort-${SNORT_VERSION}.tar.gz \
	&& tar xvfz snort-${SNORT_VERSION}.tar.gz \
	&& cd snort-${SNORT_VERSION} \
	&& ./configure --enable-sourcefire \
	&& make \
	&& sudo make install \
	&& sudo ldconfig && cd ..

#wget https://www.snort.org/downloads/community/community-rules.tar.gz
sudo mkdir /etc/snort/
#sudo tar -xf community-rules.tar.gz -C /etc/snort/
sudo tar -xf snort/snortrules-snapshot-2990.tar.gz -C /etc/snort/
sudo mv /etc/snort/etc/* /etc/snort/ \
    && sudo rm /etc/snort/snort.conf

sudo cp snort/snort.conf /etc/snort/snort.conf
sudo cp snort/local.rules /etc/snort/rules/local.rules

mkdir -p /usr/local/lib/snort_dynamicrules \
	&& mkdir -p /var/log/snort \
	&& touch /etc/snort/rules/white_list.rules \
	&& touch /etc/snort/rules/black_list.rules

sudo echo "empty" > /var/log/snort/alert

sudo cp /home/vagrant/snort/snort.service /etc/systemd/system

sudo systemctl enable snort
sudo systemctl start snort



