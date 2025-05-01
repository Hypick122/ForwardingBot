import traceback

from telethon import events
from tortoise.exceptions import DoesNotExist

from core import *
from models import MessageMap


@client.on(events.MessageDeleted(chats=[
    -1002270373322,  # D Private
    -1002508850717,  # favor
    # -1002119837460,  # test channel
]))
async def handle_message_delete(event):
    if not isinstance(event, events.MessageDeleted.Event):
        return

    try:
        for target_id in FORWARD_RULES[event.chat_id]:
            target_chat_id = TOPICS_CHAT_ID if target_id > 0 else target_id

            for deleted_id in event.deleted_ids:
                print(deleted_id)
                try:
                    message_map_id = await MessageMap.get(
                        msg_id=deleted_id,
                        is_thread=True if target_id > 0 else False
                    ).prefetch_related('orig_msg')
                except DoesNotExist:
                    print("DoesNotExist")
                    continue

                await bot.edit_message_text(
                    chat_id=target_chat_id,
                    message_id=message_map_id.sent_msg_id,
                    text=f"{message_map_id.orig_msg.text}\n\n❌ [УДАЛЕНО]",
                    parse_mode=None
                )

    except Exception:
        print("DELETE ERROR:")
        print(traceback.format_exc())
