from aiogram.types import BufferedInputFile, InputMediaDocument, \
    InputMediaVideo, InputMediaPhoto
from telethon.tl.types import DocumentAttributeFilename, DocumentAttributeAnimated
from telethon.utils import get_extension

from config import client, bot, logger
from models import *

__all__ = (
    'handle_media_message',
    'get_grouped_media'
)


def extract_filename(doc) -> str:
    return next(
        (a.file_name for a in doc.attributes if isinstance(a, DocumentAttributeFilename)),
        "file" + get_extension(doc)
    )


async def get_grouped_media(chat_id, post, max_amp=10):
    if not post.grouped_id:
        return [post] if post.media else []

    ids = range(post.id - max_amp, post.id + max_amp + 1)
    messages = await client.get_messages(chat_id, ids=ids)
    return [m for m in messages if m and m.grouped_id == post.grouped_id and m.media]


def build_input_media(msg, file: bytes, text: str):
    if msg.photo:
        return InputMediaPhoto(
            media=BufferedInputFile(file, filename="photo.jpg"),
            caption=text
        )
    elif msg.video:
        return InputMediaVideo(
            media=BufferedInputFile(file, filename="video.mp4"),
            caption=text
        )
    elif msg.document:
        name = extract_filename(msg.media.document)
        return InputMediaDocument(
            media=BufferedInputFile(file, filename=name),
            caption=text
        )

    logger.error(f"build_input_media: нет элемента\nmsg: {msg}")  # TODO: убрать
    return None


async def handle_single_message(event, send_kwargs, text: str):
    from utils.message import try_send

    message = event.message
    file = await event.download_media(file=bytes)

    if message.photo:
        return await try_send(bot.send_photo, **send_kwargs,
                              photo=BufferedInputFile(file, filename="photo.jpg"), caption=text)
    elif message.sticker:
        name = extract_filename(event.media.document)
        return await bot.send_sticker(**send_kwargs,
                                      sticker=BufferedInputFile(file, filename=name))
    elif message.video:
        is_animated = any(
            isinstance(attr, DocumentAttributeAnimated)
            for attr in message.video.attributes
        )
        if is_animated:
            return await try_send(bot.send_animation, **send_kwargs,
                                  animation=BufferedInputFile(file, filename="animation.gif"), caption=text)
        return await try_send(bot.send_video, **send_kwargs,
                              video=BufferedInputFile(file, filename="video.mp4"), caption=text)
    elif message.voice:
        return await bot.send_voice(**send_kwargs,
                                    voice=BufferedInputFile(file, filename="voice.ogg"))
    elif message.audio:
        return await bot.send_audio(**send_kwargs,
                                    audio=BufferedInputFile(file, filename="audio.mp3"))
    elif message.document:
        name = extract_filename(event.media.document)
        return await try_send(bot.send_document, **send_kwargs,
                              document=BufferedInputFile(file, filename=name), caption=text)
    return await try_send(bot.send_message, **send_kwargs, text=text)


async def handle_media_message(event, media_group, send_kwargs, target_chat_id: int):
    from utils.message import add_user_signature

    message = event.message
    text = await add_user_signature(event, target_chat_id, message.text or "")
    sent = None

    if len(media_group) > 1:
        media_to_send = []

        for msg in media_group:
            file = await client.download_media(msg, file=bytes)
            media_item = build_input_media(msg, file, text if msg.id == message.id else None)
            if media_item:
                media_to_send.append(media_item)

        if media_to_send:
            send_kwargs.pop("reply_markup")
            sent = (await bot.send_media_group(**send_kwargs, media=media_to_send))[0]

    else:
        sent = await handle_single_message(event, send_kwargs, text)

    if sent:
        messageMap = await MessageMap.create(
            chat_id=event.chat_id,
            msg_id=event.id,
            target_msg_id=sent.message_id,
            has_media=True
            # media_group_ids=[msg.message_id for msg in sent]
        )
        await OriginalMessage.create(text=event.text, message_map=messageMap)
