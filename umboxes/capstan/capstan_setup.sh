#!/usr/bin/env bash

# Download, make executable, and copy to usr/bin.
curl https://github.com/cloudius-systems/capstan/releases/download/v0.4.0/capstan
chmod ugo+x capstan
sudo cp capstan /usr/bin/
