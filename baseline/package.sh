#!/usr/bin/env bash
sudo vagrant halt
sudo vagrant package
sudo vagrant box add package.box --name kalki/umbox-baseline