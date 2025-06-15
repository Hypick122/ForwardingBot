import traceback

from telethon import events
from tortoise.exceptions import DoesNotExist

from core import *
from models import MessageMap


@client.on(events.MessageDeleted(chats=list(FORWARD_RULES.keys())))
# @client.on(events.MessageDeleted(chats=[
#     -1002270373322,  # D Private
#     -1002508850717,  # favor
#     -1002506549679,  # Приватка REKT BOYS
#     # -1002119837460,  # test channel
# ]))
async def handle_message_delete(event):
    if not isinstance(event, events.MessageDeleted.Event):
        return

    try:
        for target_id in FORWARD_RULES[event.chat_id]:
            target_chat_id = TOPICS_CHAT_ID if target_id > 0 else target_id

            for deleted_id in event.deleted_ids:
                try:
                    message_map_id = await MessageMap.get(
                        chat_id=event.chat_id,
                        msg_id=deleted_id,
                        is_thread=True if target_id > 0 else False
                    ).prefetch_related('orig_msg')
                except DoesNotExist:
                    continue

                if message_map_id.has_media:
                    await bot.edit_message_caption(
                        chat_id=target_chat_id,
                        message_id=message_map_id.sent_msg_id,
                        caption=f"{message_map_id.orig_msg.text}\n\n❌ [УДАЛЕНО]",
                        parse_mode="Markdown"
                    )
                else:
                    await bot.edit_message_text(
                        chat_id=target_chat_id,
                        message_id=message_map_id.sent_msg_id,
                        text=f"{message_map_id.orig_msg.text}\n\n❌ [УДАЛЕНО]",
                        parse_mode="Markdown"
                    )

    except Exception:
        print("\nDELETE ERROR:")
        print("event: ", event)
        print("FORWARD_RULES[event.chat_id]: ", FORWARD_RULES[event.chat_id])
        print(traceback.format_exc())
