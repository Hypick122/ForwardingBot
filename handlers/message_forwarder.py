import traceback
from datetime import datetime

from telethon import events

from core import *


@client.on(events.NewMessage(chats=list(FORWARD_RULES.keys())))
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

    if type(FORWARD_RULES[chat_id]) is dict and reply_to_top_id not in FORWARD_RULES[chat_id].keys():
        return

    forward_targets = FORWARD_RULES[chat_id] if type(FORWARD_RULES[chat_id]) is list else FORWARD_RULES[chat_id][
        reply_to_top_id]

    try:
        for target_id in forward_targets:
            target_chat_id = TOPICS_CHAT_ID if target_id > 0 else target_id
            thread_id = target_id if target_id > 0 else None

            await send_message(target_chat_id, event, thread_id=thread_id)
    except Exception as e:
        print("\nFORWARDING ERROR:")
        print("chat_id: ", chat_id)
        print("reply_to_top_id: ", reply_to_top_id)
        print("event: ", event)
        print("forward_targets: ", forward_targets)
        print(traceback.format_exc())
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('errors.txt', 'a', encoding='utf-8') as f:
            f.write(f'[{now}] Ошибка хендлера:\n')
            f.write(f'forward_targets: {forward_targets}\n')
            f.write(f'Event: {event}\n')
            f.write(f'Ошибка: {str(e)}\n')
            f.write('Traceback:\n')
            f.write(traceback.format_exc())
            f.write('\n' + '=' * 80 + '\n')
