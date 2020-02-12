#!/usr/bin/env bash
sudo vagrant destroy -f
sudo vagrant up
sudo bash ../vm_create_image.sh
bash ../vm_deploy.sh
