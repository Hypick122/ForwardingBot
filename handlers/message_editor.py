import traceback

from telethon import events
from tortoise.exceptions import DoesNotExist

from core import *
from models import MessageMap


@client.on(events.MessageEdited(chats=list(FORWARD_RULES.keys())))
async def handle_message_edit(event):
    if not isinstance(event, events.MessageEdited.Event):
        return

    chat_id = event.chat_id

    reply_to_top_id = None
    if event.reply_to:
        if event.reply_to.reply_to_top_id:
            reply_to_top_id = event.reply_to.reply_to_top_id
        elif event.reply_to.forum_topic:
            reply_to_top_id = event.reply_to.reply_to_msg_id

    if (type(FORWARD_RULES[chat_id]) is dict and reply_to_top_id not in FORWARD_RULES[chat_id].keys()
            or chat_id == -1002408242605 and reply_to_top_id is not [9282]
            or chat_id == -1002361161091 and reply_to_top_id is not [2981, 9]
            or chat_id == -1002293398473 and reply_to_top_id is [679, 674, 5914]):
        # print("skip\n")
        return

    forward_targets = FORWARD_RULES[chat_id] if type(FORWARD_RULES[chat_id]) is list else FORWARD_RULES[chat_id][
        reply_to_top_id]

    try:
        for target_id in forward_targets:
            target_chat_id = TOPICS_CHAT_ID if target_id > 0 else target_id

            try:
                message_map_id = await MessageMap.get(
                    chat_id=event.chat_id,
                    msg_id=event.id,
                    is_thread=True if target_id > 0 else False
                ).prefetch_related('orig_msg')
            except DoesNotExist:
                continue

            cleaned_text = remove_lines_by_keywords(event.text, KEYWORDS_TO_REMOVE)

            if message_map_id.has_media:
                await bot.edit_message_caption(
                    chat_id=target_chat_id,
                    message_id=message_map_id.sent_msg_id,
                    caption=cleaned_text or "",
                    parse_mode="Markdown"
                )
            else:
                await bot.edit_message_text(
                    chat_id=target_chat_id,
                    message_id=message_map_id.sent_msg_id,
                    text=cleaned_text or "",
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
    except Exception:
        print("\nEDIT ERROR:")
        print("chat_id: ", chat_id)
        print("reply_to_top_id: ", reply_to_top_id)
        print("event: ", event)
        print("forward_targets: ", forward_targets)
        print(traceback.format_exc())
