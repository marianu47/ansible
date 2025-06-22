#!/bin/bash
sudo apt update -yq
sudo apt install ansible -yq
sudo ansible-galaxy collection install google.cloud community.crypto community.general community.google
