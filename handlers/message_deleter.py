from telethon import events

from config import client, TOPICS_CHAT_ID
from utils import *


@client.on(events.MessageDeleted())
async def handle_message_delete(event):
    if not isinstance(event, events.MessageDeleted.Event):
        return

    chat_id = event.chat_id
    if chat_id not in await get_monitored_channels():
        return

    forward_targets = await get_forward_targets(chat_id)
    if not forward_targets:  # TODO: исправь удаление в топиках
        return

    for target_id in forward_targets:
        target_chat_id = TOPICS_CHAT_ID if target_id > 0 else target_id
        is_thread = target_id > 0

        for deleted_id in event.deleted_ids:
            message_map = await safe_get_message_map(chat_id, deleted_id, is_thread)
            if not message_map:
                continue

            updated_text = f"{message_map.orig_msg.text}\n\n❌ [УДАЛЕНО]"
            await edit_forwarded_message(target_chat_id, message_map.sent_msg_id, updated_text, message_map.has_media)
