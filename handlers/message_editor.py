import traceback
from datetime import datetime

from aiogram.exceptions import TelegramBadRequest
from telethon import events

from config import client, TOPICS_CHAT_ID
from utils import *


@client.on(events.MessageEdited())
async def handle_message_edit(event):
    if not isinstance(event, events.MessageEdited.Event):
        return

    chat_id = event.chat_id
    if chat_id not in await get_monitored_channels():
        return

    thread_id = get_thread_id(event)
    if (thread_id and
            ((chat_id == -1002408242605 and thread_id != 9282) or
             (chat_id == -1002361161091 and thread_id not in [2981, 9]) or
             (chat_id == -1002293398473 and thread_id in [679, 674, 5914]))):
        return

    forward_targets = await get_forward_targets(chat_id, thread_id)
    if not forward_targets:
        return

    for target_id in forward_targets:
        target_chat_id = TOPICS_CHAT_ID if target_id > 0 else target_id
        is_thread = target_id > 0

        message_map = await safe_get_message_map(chat_id, event.id, is_thread)
        if not message_map:
            continue

        try:
            cleaned_text = remove_keywords_lines(event.text, await get_keywords_to_remove())
            updated_text = await append_user_signature(event, target_chat_id, target_id if is_thread else None,
                                                       cleaned_text)

            await edit_forwarded_message(target_chat_id, message_map.sent_msg_id, updated_text, message_map.has_media)
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise
