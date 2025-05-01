import traceback
from datetime import datetime

from telethon import events

from core import *


@client.on(events.NewMessage(chats=[
    -1002164115278,  # Finder
    -1002408242605,  # Furious
    -1002270373322,  # D Private
    -1002361161091,  # Genesis
    -1002508850717,  # favor
    -1002519569203,  # favor chat
    # -1002119837460,  # test channel
]))
async def handle_message_forwarding(event):
    if not isinstance(event, events.NewMessage.Event):
        return

    chat_id = event.chat_id

    reply_to_top_id = None
    if event.reply_to:
        if event.reply_to.reply_to_top_id:
            reply_to_top_id = event.reply_to.reply_to_top_id
        elif event.reply_to.forum_topic:
            reply_to_top_id = event.reply_to.reply_to_msg_id

    if chat_id in ALLOWED_TOPICS and reply_to_top_id not in ALLOWED_TOPICS.get(chat_id, []):
        return

    forward_targets = FORWARD_RULES[chat_id] if chat_id not in ALLOWED_TOPICS else FORWARD_RULES[chat_id][
        reply_to_top_id]

    try:
        for target_id in forward_targets:
            target_chat_id = TOPICS_CHAT_ID if target_id > 0 else target_id
            thread_id = target_id if target_id > 0 else None

            await send_message(target_chat_id, event, thread_id=thread_id)
    except Exception as e:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('errors.txt', 'a', encoding='utf-8') as f:
            f.write(f'[{now}] Ошибка хендлера:\n')
            f.write(f'forward_targets: {forward_targets}\n')
            f.write(f'Event: {event}\n')
            f.write(f'Ошибка: {str(e)}\n')
            f.write('Traceback:\n')
            f.write(traceback.format_exc())
            f.write('\n' + '=' * 80 + '\n')
