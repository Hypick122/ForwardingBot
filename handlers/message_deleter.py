from telethon import events

from config import client
from utils import *


@client.on(events.MessageDeleted())
async def handle_message_delete(event):  # TODO: удаление в топиках неисправна
    if not isinstance(event, events.MessageDeleted.Event):
        return

    chat_id = event.chat_id
    if chat_id not in await get_monitored_channels():
        return

    forward_targets = await get_forward_targets(chat_id)
    if not forward_targets:
        return

    for deleted_id in event.deleted_ids:
        message_map = await safe_get_message_map(chat_id, deleted_id)
        if not message_map:
            continue

        updated_text = f"{message_map.orig_msg.text}\n\n❌ [УДАЛЕНО]"
        await edit_forwarded_message(
            forward_targets.target_chat_id,
            message_map.target_msg_id,
            updated_text,
            message_map.has_media
        )
