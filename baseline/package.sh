#!/usr/bin/env bash
sudo vagrant package baseline.box
sudo vagrant box add baseline.box --name kalki/umbox-baseline