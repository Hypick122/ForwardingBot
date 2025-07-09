from telethon import events

from config import client, TOPICS_CHAT_ID
from utils import *


@client.on(events.NewMessage())
async def handle_message_forwarding(event):
    if not isinstance(event, events.NewMessage.Event):
        return

    chat_id = event.chat_id
    if chat_id not in await get_monitored_channels():
        return

    thread_id = get_thread_id(event)
    forward_targets = await get_forward_targets(chat_id, thread_id)
    if not forward_targets:
        return

    is_skip = await get_bypass_skip(chat_id, thread_id)
    if any(keyword in event.text for keyword in await get_keywords_to_skip()) and is_skip:
        return

    for target_id in forward_targets:
        target_chat_id = TOPICS_CHAT_ID if target_id > 0 else target_id
        target_thread_id = target_id if target_id > 0 else None
        await send_message(event, target_chat_id, target_thread_id)
