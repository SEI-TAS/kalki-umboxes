#!/usr/bin/env bash
sudo vagrant destroy -f
sudo vagrant up
sudo bash ../create_standalone_image.sh
bash ../deploy.sh
