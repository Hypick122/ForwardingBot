import traceback

from telethon import events
from tortoise.exceptions import DoesNotExist

from core import *
from models import MessageMap


@client.on(events.MessageEdited(chats=list(FORWARD_RULES.keys())))
async def handle_message_edit(event):
    if not isinstance(event, events.MessageEdited.Event):
        return

    try:
        # markup = convert_telethon_markup_to_aiogram(event.reply_markup) if event.reply_markup else None

        for target_id in FORWARD_RULES[event.chat_id]:
            target_chat_id = TOPICS_CHAT_ID if target_id > 0 else target_id

            try:
                message_map_id = await MessageMap.get(
                    msg_id=event.id,
                    is_thread=True if target_id > 0 else False
                ).prefetch_related('orig_msg')
            except DoesNotExist:
                continue

            print("orig text: ", message_map_id.orig_msg.text)
            print("new text: ", event.text)

            if message_map_id.orig_msg.text == event.text:
                print("skip edit")
                return

            await bot.edit_message_text(
                chat_id=target_chat_id,
                message_id=message_map_id.sent_msg_id,
                text=event.text or "",
                # reply_markup=markup,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )

    except Exception:
        print("EDIT ERROR:")
        print("event: ", event)
        print(traceback.format_exc())
