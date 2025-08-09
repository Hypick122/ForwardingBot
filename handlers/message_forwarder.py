from tortoise.exceptions import DoesNotExist

from config import bot
from models import *
from utils import *


async def prepare_text_and_entities(event, fwd_rule):  # TODO: перенести в utils message
    text = event.raw_text or ""
    extra_entities = []

    okx_links = parse_okx_link(event.text)
    if okx_links:
        text += f"\n{okx_links}"

    metascalp_links = parse_exchange_links(event.text)
    if metascalp_links:
        text += "\n" + "\n".join(metascalp_links)
        extra_entities = build_code_entities(text, metascalp_links)

    removal_keywords = await get_removal_keywords()
    cleaned_text = remove_keywords_lines(text, removal_keywords)
    text_with_author = await add_author(event, fwd_rule, cleaned_text)

    base_entities = telethon_entities_to_aiogram(event.entities or [])
    entities = base_entities + extra_entities

    return text_with_author, entities


async def handle_message_forwarding(event):
    chat_id = event.chat_id
    thread_id = get_thread_id(event)
    fwd_rule = await get_forward_rule(chat_id, thread_id)
    if not fwd_rule:
        return
    print("\nchat_id", chat_id)
    print("thread_id", thread_id)
    print("fwd_rule", fwd_rule)
    print("event", event)

    is_skip = await get_skip_flag(chat_id, thread_id)
    check_skip_text = await check_skip_keywords(event.text)  # TODO: плохо работает с форматированием (event.raw_text)
    if is_skip and check_skip_text:
        return

    text, entities = await prepare_text_and_entities(event, fwd_rule)

    send_kwargs = {
        "chat_id": fwd_rule.target_chat_id,
        "reply_markup": telethon_markup_to_aiogram(event.reply_markup) if event.reply_markup else None
    }

    if event.reply_to:
        try:
            message_map = await MessageMap.get(
                chat_id=event.chat_id,
                msg_id=event.reply_to.reply_to_msg_id
            )
            send_kwargs["reply_to_message_id"] = message_map.target_msg_id
        except DoesNotExist:
            pass

    if event.message.media:
        send_kwargs["caption_entities"] = entities
        media_group = await get_grouped_media(event.chat_id, event.message)

        if len(media_group) > 1 and event.message.id == media_group[0].id:
            await handle_media_message(event, fwd_rule, media_group, send_kwargs)
        elif len(media_group) <= 1:
            await handle_media_message(event, fwd_rule, [event.message], send_kwargs)
        return

    send_kwargs["entities"] = entities
    send_kwargs["disable_web_page_preview"] = True

    sent = await bot.send_message(**send_kwargs, text=text)

    messageMap = await MessageMap.create(
        chat_id=event.chat_id,
        msg_id=event.id,
        target_msg_id=sent.message_id
    )
    await OriginalMessage.create(text=text, message_map=messageMap)
