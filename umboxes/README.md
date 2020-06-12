# Umboxes

## Overview

This folder contains a series of configurations and scripts used to create either VM-based or container-based umboxes.
All the folders inside "standard" contain configurations for specific umboxes. The rest of the folders inside the "common"
folder have supporting common configs or scripts to help in creating them. More specifically:

- **alerter_docker**: has a script and Docker config to create an alerter container.
- **alerter_vm_base**: has scripts and configurations for the alerter to go inside a VM-based umbox.
- **sniffer_docker**: has a script and Docker config to create an sniffer container, as well as common things for container
umboxes based on the sniffer.
- **sniffer_vm_base**: has scripts and configurations for the sniffer to go inside a VM-based umbox.
- **snort_base**: common configs for a snort-based umbox.

All umboxes are created with four NICs: 
- One (eth0) connected to the control plane through a virtual switch to the control node
- Two (eth1 and eth2) connected to the data plane through the OVS switch (one for incoming, one for outgoing traffic)
- A fourth one (eth3) that can be used to send replies directly to an external endpoint and skip the rest of a chain of umboxes

**VM-Based Umboxes**: These umboxes are Virtual Machines that run on the qemu-kvm hypervisor.
The process of creating an umboxes entails creating a qcow2 disk image that can be used by qemu-kvm. Other VM details are defined and created by the Controller when starting an umbox. Current disk images are based on Ubuntu 16.04.

**Docker-Based Umboxes**: These umboxes are Docker containers running the appropriate software.
The process entails creating a docker image for each umbox, which will be stored in the local docker image repo.
They are based on the python:3.5 image.

## Pre-Requisites
### VM-Based Umboxes: Vagrant
Before creating a disk image, Vagrant needs to be properly set up. This needs to be done only once per environment.

1. Install Vagrant, qemu and libvirt on the computer where creating the Umbox. If Ubuntu:
    1. `bash setup_vagrant.sh`
    1. Ensure that libvirt and qemu are working properly (i.e., test with something like "virsh list").
    1. You may need to install a newer vagrant version if there are issues with the distribution one; https://www.vagrantup.com/downloads.html

1. Install the Vagrant libvirt plugin (details here: https://github.com/vagrant-libvirt/vagrant-libvirt#installation)
    1. `sudo apt-get build-dep vagrant ruby-libvirt `
        - (See this link if you have issues: https://askubuntu.com/questions/826890/apt-build-dep-fails-unable-to-locate-source-package-despite-deb-src-lines-pres)
    1. `sudo apt-get install qemu libvirt-bin ebtables dnsmasq-base`
    1. `sudo apt-get install libxslt-dev libxml2-dev libvirt-dev zlib1g-dev ruby-dev`
    1. `vagrant plugin install vagrant-libvirt`

### Docker-Based Umboxes: Docker
Before creating a docker image, Docker needs to be properly set up. This needs to be done only once per environment.

1. Install Docker.
1. Ensure proxies are properly configured, if needed.
    1. Docker Image Download: needs to be setup for Docker to properly download images. See: https://stackoverflow.com/questions/23111631/cannot-download-docker-images-behind-a-proxy
    1. Docker Image Creation: needs to be setup so that commands called inside a container when building an image work properly. See: https://docs.docker.com/network/proxy/

## Setting up Umbox Components and Structure
The overall structure for the umbox files needs to be set up first.

1. Clone this repo.
1. Create a new subfolder for the new umbox inside that repo, inside the folder `standard`. This new folder should only have letters, numbers, and hyphens, and start with "uN" where N is a number for the umbox, followed by a short name related to the function of the umbox. Example: u13-proxy-block.
1. Define what network software will be running in that umbox. 
    1. Ensure that network software outputs issues that should become alerts to a log file, and that some specific keyword can be used to find instances of this in the log file.
    1. Ensure that it echoes the packets it receives back out of the umbox through eth2.
    1. Add any non-downloadable files for this software to your folder.
    1. You will define how to setup this software in the next steps.

The remaining steps depend on whether the VM will be based on the common Sniffer code, or will use some different software.
1. Sniffer-based:
    1. Copy `/sniffer/config.json` as `config.json` into your umbox folder. Then configure as needed for the Sniffer features you want to use. See the readme in the sniffer folder for details.
    1. If you want to have a configuration for a VM-based version of the umbox, copy the file `Vagrantfile` from another umbox to your folder. No changes are needed in this file.
    1. No additional config is needed if you want to build a Docker-based version of the umbox.
1. Non-sniffer based:
    1. Copy `/alerter/config.json` into your folder as `config_alerter.json`, and configure it. See the readme in that folder for details.
    1. If you want to have a configuration for a VM-based version of the umbox:
        1. Copy the file `Vagrantfile` from `common/sniffer_vm_base` to your folder, and modify the `Vagrant.configure` section as needed
            1. Copy all needed files using Vagrantfile commands
            1. If you need to execute commands to set up your software, execute them directly in the Vagrantfile or form a script and call them from the Vagrantfile
            1. Be sure to configure your software to automatically start on machine boot (such as creating a systemd service)
    1. If you want to build a Docker-based version of the umbox:
        1. Copy the `Dockerfile` file from `common/sniffer_docker` to your folder
        1. Leave the first line as it is, modify the rest of the file to set up your network software

## Creating an Umbox Image

### VM-Based
1. Modify `vm_deploy.sh` by setting the UMBOX_IMAGES_FOLDER variable to the folder where you want the disk image to end up.
1. Go to your umbox's folder, and execute the following, waiting for it to finish successfully (it can take several minutes):
    1. `sudo bash ../../vm_full_process.sh`

### Docker-Based
1. Ensure that the base Alerter image (kalki/alerter) exists. This only needs to be done once per environment, or each time the Alerter is modified.
    1. Go to `common/alerter_docker`
    1. Execute the following:
        - `bash build_alerter_image.sh`
1. **ONLY** for Sniffer-based umboxes, ensure that the base Sniffer image (kalki/sniffer) exists. This only needs to be done once per environment, or each time the Sniffer is modified.
    1. Go to `common/sniffer_docker`
    1. Execute the following:
        - `bash build_sniffer_image.sh`
1. Go to your umbox's folder, and execute the following:
    1. Sniffer-based:
        - `bash ../../common/sniffer_docker/build_umbox_image.sh`
        - This will create a Docker image in the local repo with a name equal to the umbox folder's name.
    2. Not sniffer-based:
        1. Use a `docker build` command to build your umbox based on your Dockerfile.
1. Go to the `deployments` folder, and choose one deployment config to use from the subfolders there. Then execute:
    - `bash build_umbox_image.sh <image_name> <deployment_name>` where
       - <image_name> is the name of the docker image of the umbox created in the previous step
       - <deployment> is the name of a subfolder that contains the appropriate alerter configuration for that deployment
