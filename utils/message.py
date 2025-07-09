from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from telethon.tl.types import ReplyInlineMarkup, KeyboardButtonUrl, User
from tortoise.exceptions import DoesNotExist

from config import *
from models import *

__all__ = (
    'send_message',
    'remove_keywords_lines',
    'get_thread_id',
    'append_user_signature',
    'try_send',
    'edit_forwarded_message',
)


async def send_message(event, target_chat_id: int, target_thread_id: int = None):
    from utils import get_grouped_media, handle_media_message, get_keywords_to_remove
    message = event.message
    text = message.text or ""
    markup = telethon_to_aiogram_markup(event.reply_markup) if event.reply_markup else None

    send_kwargs = {
        "chat_id": target_chat_id,
        "reply_markup": markup
    }

    if event.reply_to:
        try:
            message_map = await MessageMap.get(
                chat_id=event.chat_id,
                msg_id=event.reply_to.reply_to_msg_id,
                is_thread=bool(target_thread_id)
            )
            send_kwargs["reply_to_message_id"] = message_map.sent_msg_id
        except DoesNotExist:
            pass

    if target_thread_id:
        send_kwargs["message_thread_id"] = target_thread_id

    if message.media:
        media_group = await get_grouped_media(event.chat_id, message)
        if len(media_group) > 1 and message.id == media_group[0].id:
            await handle_media_message(event, media_group, send_kwargs, target_chat_id, target_thread_id)
        elif len(media_group) <= 1:
            await handle_media_message(event, [message], send_kwargs, target_chat_id, target_thread_id)
    else:
        send_kwargs["disable_web_page_preview"] = True

        cleaned_text = remove_keywords_lines(text, await get_keywords_to_remove())
        cleaned_text = await append_user_signature(event, target_chat_id, target_thread_id, cleaned_text)
        sent = await try_send(bot.send_message, **send_kwargs, text=cleaned_text)

        messageMap = await MessageMap.create(
            chat_id=event.chat_id,
            msg_id=event.id,
            sent_msg_id=sent.message_id,
            is_thread=bool(target_thread_id)
        )
        await OriginalMessage.create(text=cleaned_text, message_map=messageMap)


def telethon_to_aiogram_markup(markup: ReplyInlineMarkup) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=btn.text, url=btn.url)
         for btn in row.buttons if isinstance(btn, KeyboardButtonUrl)]
        for row in markup.rows
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_thread_id(event):
    if event.reply_to:
        if event.reply_to.reply_to_top_id:
            return event.reply_to.reply_to_top_id
        elif event.reply_to.forum_topic:
            return event.reply_to.reply_to_msg_id

    return None


def remove_keywords_lines(text: str, keywords: list[str]) -> str:
    return "\n".join(
        line for line in text.strip().splitlines()
        if not any(kw in line for kw in keywords)
    )


async def append_user_signature(event, chat_id, thread_id, text):
    allow = chat_id in [-1002357512003, -1002602282145] or thread_id in [50, 98, 34003, 2671]
    if not allow:
        return text

    logger.debug("append_user_signature")
    user = await client.get_entity(event.from_id.user_id)
    logger.debug("user", user)
    # try:
    #     user = await client.get_entity(event.sender_id)
    # except Exception:
    #     try:
    #         user = await client.get_entity(event.from_id.user_id)
    #     except Exception:
    #         return text

    if not isinstance(user, User):
        return text

    if user.bot:
        name = "bot"
    elif user.username:
        name = f"@{user.username}"
    else:
        name = (user.first_name or '') + ' ' + (user.last_name or '')

    return f"{text}\n\nBy {name.strip() or f'(ID) {event.from_id.user_id}'}"


async def try_send(send_func, *args, **kwargs):
    try:
        return await send_func(*args, **kwargs)
    except TelegramBadRequest:
        kwargs["parse_mode"] = None
        return await send_func(*args, **kwargs)


async def edit_forwarded_message(target_chat_id, sent_msg_id, text, has_media):
    if has_media:
        await try_send(bot.edit_message_caption, chat_id=target_chat_id, message_id=sent_msg_id, caption=text)
    else:
        await try_send(bot.edit_message_text, chat_id=target_chat_id, message_id=sent_msg_id, text=text,
                       disable_web_page_preview=True)
