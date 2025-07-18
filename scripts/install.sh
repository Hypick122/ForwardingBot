#!/usr/bin/bash

# Обновление и установка пакетов
sudo apt update && sudo apt upgrade -y
sudo apt install tmux p7zip-full python3.12 python3.12-venv python3-pip -y

# Распаковка и настройка окружения
7z x -y ForwardingBot.7z && cd ForwardingBot || exit 1
python3 -m venv venv

# Установка зависимостей
source venv/bin/activate
pip install --upgrade pip && pip install -r requirements.txt

# chmod +x install.sh run.sh