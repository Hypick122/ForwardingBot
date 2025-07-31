#!/usr/bin/bash

sudo apt update && sudo apt upgrade -y
sudo apt install tmux dos2unix p7zip-full python3.12 python3.12-venv python3-pip -y

7z x -y ForwardingBot.7z && cd ForwardingBot || exit 1
dos2unix scripts/run.sh
python3 -m venv venv

source venv/bin/activate
pip install --upgrade pip && pip install -r requirements.txt

# chmod +x install.sh run.sh