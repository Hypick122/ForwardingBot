from aiogram.types import BufferedInputFile, InputMediaDocument, \
    InputMediaVideo, InputMediaPhoto
from telethon.tl.types import DocumentAttributeFilename, DocumentAttributeAnimated
from telethon.utils import get_extension

from config import *
from models import *

__all__ = (
    'handle_media_message',
    'get_grouped_media'
)


def extract_filename(doc):
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


async def handle_media_message(event, media_group, send_kwargs, target_chat_id, thread_id):
    from utils.message import try_send, append_user_signature
    message = event.message
    text = await append_user_signature(event, target_chat_id, thread_id, message.text or "")

    if len(media_group) > 1:
        media_to_send = []
        for msg in media_group:
            file = await client.download_media(msg, file=bytes)

            if msg.photo:
                media_to_send.append(
                    InputMediaPhoto(
                        media=BufferedInputFile(file, filename="photo.jpg"),
                        caption=text if msg.id == message.id else None
                    )
                )
            elif msg.video:
                media_to_send.append(
                    InputMediaVideo(
                        media=BufferedInputFile(file, filename="video.mp4"),
                        caption=text if msg.id == message.id else None
                    )
                )
            elif msg.document:
                name = extract_filename(msg.media.document)
                media_to_send.append(
                    InputMediaDocument(
                        media=BufferedInputFile(file, filename=name),
                        caption=text if msg.id == message.id else None
                    )
                )

        if media_to_send:
            send_kwargs.pop("reply_markup")
            sent = (await bot.send_media_group(**send_kwargs, media=media_to_send))[0]

    else:
        file = await event.download_media(file=bytes)

        if message.photo:
            sent = await try_send(bot.send_photo, **send_kwargs,
                                  photo=BufferedInputFile(file, filename="photo.jpg"), caption=text)
        elif message.sticker:
            name = extract_filename(event.media.document)
            sent = await bot.send_sticker(**send_kwargs, sticker=BufferedInputFile(file, filename=name))
        elif message.video:
            is_animated = any(
                isinstance(attr, DocumentAttributeAnimated)
                for attr in message.video.attributes
            )
            if is_animated:
                sent = await try_send(bot.send_animation, **send_kwargs,
                                      animation=BufferedInputFile(file, filename="animation.gif"), caption=text)
            else:
                sent = await try_send(bot.send_video, **send_kwargs,
                                      video=BufferedInputFile(file, filename="video.mp4"), caption=text)
        elif message.voice:
            sent = await bot.send_voice(**send_kwargs, voice=BufferedInputFile(file, filename="voice.ogg"))
        elif message.audio:
            sent = await bot.send_audio(**send_kwargs, audio=BufferedInputFile(file, filename="audio.mp3"))
        elif message.document:
            name = extract_filename(event.media.document)
            sent = await try_send(bot.send_document, **send_kwargs,
                                  document=BufferedInputFile(file, filename=name), caption=text)
        else:
            sent = await try_send(bot.send_message, **send_kwargs, text=text)

    messageMap = await MessageMap.create(
        chat_id=event.chat_id,
        msg_id=event.id,
        sent_msg_id=sent.message_id,
        is_thread=bool(thread_id),
        has_media=True
        # media_group_ids=[msg.message_id for msg in sent]
    )
    await OriginalMessage.create(text=event.text, message_map=messageMap)
