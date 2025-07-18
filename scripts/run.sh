#!/usr/bin/bash

source venv/bin/activate

tmux has-session -t forwarding_bot 2>/dev/null && {
    echo "Перезапуск существующей сессии..."
    tmux kill-session -t forwarding_bot
    sleep 1
}

tmux new -d -s forwarding_bot "python3 ./__main__.py"

# tmux attach -t forwarding_bot