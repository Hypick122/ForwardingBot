from aiogram.exceptions import TelegramBadRequest
from telethon import events

from config import client
from utils import *


@client.on(events.MessageEdited())
async def handle_message_edit(event):
    if not isinstance(event, events.MessageEdited.Event):
        return

    chat_id = event.chat_id
    if chat_id not in await get_monitored_channels():
        return

    thread_id = get_thread_id(event)
    # TODO: проверить
    forward_targets = await get_forward_targets(chat_id, thread_id)
    if not forward_targets:
        return

    message_map = await safe_get_message_map(chat_id, event.id)
    if not message_map:
        return

    try:
        cleaned_text = remove_keywords_lines(event.text, await get_keywords_to_remove())
        updated_text = await add_user_signature(event, forward_targets.target_chat_id, cleaned_text)
        await edit_forwarded_message(
            forward_targets.target_chat_id,
            message_map.target_msg_id,
            updated_text,
            message_map.has_media
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
