from aiogram.exceptions import TelegramBadRequest

from utils import *


async def handle_message_edit(event):
    chat_id = event.chat_id
    thread_id = get_thread_id(event)
    fwd_rule = await get_forward_rule(chat_id, thread_id)
    if not fwd_rule:
        return

    message_map = await get_message_map_safe(chat_id, event.id)
    if not message_map:
        return

    try:
        cleaned_text = remove_keywords_lines(event.text, await get_removal_keywords())  # TODO: заменить на raw_text или добавить entities в бд
        text = await add_author(event, fwd_rule, cleaned_text)
        await edit_forwarded_message(
            fwd_rule.target_chat_id,
            message_map.target_msg_id,
            text,
            message_map.has_media
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
