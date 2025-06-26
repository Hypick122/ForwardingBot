import traceback

from telethon import events
from tortoise.exceptions import DoesNotExist

from core import *
from models import MessageMap


@client.on(events.MessageDeleted())
async def handle_message_delete(event):
    if not isinstance(event, events.MessageDeleted.Event):
        return

    chat_id = event.chat_id
    if chat_id not in await get_monitored_channels():
        return

    forward_targets = await get_forward_targets(chat_id)
    if not forward_targets:
        return

    for target_id in forward_targets:
        target_chat_id = TOPICS_CHAT_ID if target_id > 0 else target_id
        try:
            for deleted_id in event.deleted_ids:
                try:
                    message_map_id = await MessageMap.get(
                        chat_id=chat_id,
                        msg_id=deleted_id,
                        is_thread=True if target_id > 0 else False
                    ).prefetch_related('orig_msg')
                except DoesNotExist:
                    continue

                if message_map_id.has_media:
                    await bot.edit_message_caption(
                        chat_id=target_chat_id,
                        message_id=message_map_id.sent_msg_id,
                        caption=f"{message_map_id.orig_msg.text}\n\n❌ [УДАЛЕНО]"
                    )
                else:
                    await bot.edit_message_text(
                        chat_id=target_chat_id,
                        message_id=message_map_id.sent_msg_id,
                        text=f"{message_map_id.orig_msg.text}\n\n❌ [УДАЛЕНО]"
                    )

        except Exception:
            print("\nDELETE ERROR:")
            print("event: ", event)
            print("FORWARD_RULES[chat_id]: ", get_forward_targets(chat_id))
            print(traceback.format_exc())
