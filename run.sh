#!/bin/bash

# sudo apt update && sudo apt upgrade -y
# sudo apt install p7zip-full python3.10 python3.10-venv python3.10-dev python3-pip -y

# 7z x ForwardingBot.7z
# cd ForwardingBot

# python3 -m venv venv
source venv/bin/activate

# pip install --upgrade pip
# pip install -r requirements.txt

python3 __main__.py

# chmod +x run.sh
# nohup ./run.sh &
# nohup python3 __main__.py &
# pkill -f "__main__.py"