import traceback

from telethon import events
from tortoise.exceptions import DoesNotExist

from core import *
from models import MessageMap


@client.on(events.MessageEdited(chats=[
    -1002270373322,  # D Private
    -1002508850717,  # favor
    # -1002119837460,  # test channel
]))
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
                )
            except DoesNotExist:
                continue

            print("EDIT")
            print("target_chat_id: ", target_chat_id)
            print("message_map_id.sent_msg_id: ", message_map_id.sent_msg_id)
            print("event.text or "": ", event.text or "")
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
        print(traceback.format_exc())
