import traceback
from datetime import datetime

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile, InputMediaDocument, \
    InputMediaVideo, InputMediaPhoto
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import ReplyInlineMarkup, KeyboardButtonUrl, DocumentAttributeFilename
from telethon.utils import get_extension
from tortoise.exceptions import DoesNotExist

from core.config import *
from models import *

__all__ = (
    'connect_to_session',
    'send_message',
    'convert_telethon_markup_to_aiogram',
    'get_filename_from_doc',
    'remove_lines_by_keywords',
    'get_monitored_channels',
    'get_forward_targets',
    'get_keywords_to_remove',
    'get_keywords_to_skip',
    'get_channel_bypass_skip',
    'get_thread_bypass_skip'
)


async def connect_to_session() -> None:
    await client.connect()

    if not await client.is_user_authorized():
        print('[*] Пользователь не авторизован. Начинаем процесс входа...')
        await client.send_code_request(config.PHONE)
        code = input('Введите код, полученный в Telegram: ')

        try:
            await client.sign_in(config.PHONE, code)
        except SessionPasswordNeededError:
            password = input('Введите пароль двухфакторной аутентификации: ')
            await client.sign_in(password=password)

        print('[+] Авторизация прошла успешно. Сессия сохранена.')
    else:
        print('[✓] Сессия уже авторизована. Повторная авторизация не требуется.')

    me = await client.get_me()
    print(f"👤 Вы вошли как: {me.first_name} ({me.username})")


async def send_message(target_chat_id: int, event, thread_id: int = None):
    try:
        message = event.message
        text = message.text or ""
        markup = convert_telethon_markup_to_aiogram(event.reply_markup) if event.reply_markup else None

        send_kwargs = {
            "chat_id": target_chat_id,
            "reply_markup": markup
        }

        if event.reply_to:
            try:
                message_map_id = await MessageMap.get(
                    chat_id=event.chat_id,
                    msg_id=event.reply_to.reply_to_msg_id,
                    is_thread=bool(thread_id)
                )
                send_kwargs["reply_to_message_id"] = message_map_id.sent_msg_id
            except DoesNotExist:
                pass

        if any(keyword in event.text for keyword in
               await get_keywords_to_skip()) and thread_id not in await get_thread_bypass_skip() and event.chat_id not in await get_channel_bypass_skip():
            return

        if thread_id:
            send_kwargs["message_thread_id"] = thread_id

        if message.media:
            media_group = await _get_media_posts_in_group(event.chat_id, message)
            if len(media_group) > 1 and message.id == media_group[0].id:
                await handle_media_message(event, media_group, send_kwargs, thread_id)
            elif len(media_group) <= 1:
                await handle_media_message(event, [message], send_kwargs, thread_id)
        else:
            send_kwargs["disable_web_page_preview"] = True
            # send_kwargs["parse_mode"] = "Markdown"

            cleaned_text = remove_lines_by_keywords(text, await get_keywords_to_remove())
            if target_chat_id in [-1002357512003, -1002602282145] or thread_id in [50, 98, 34003, 2672]:
                try:
                    user = await client.get_entity(event.from_id.user_id)

                    if user.username:
                        name = f"@{user.username}"
                    elif user.first_name or user.last_name:
                        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                    else:
                        name = f"(ID) {event.from_id.user_id}"

                    cleaned_text += f"\n\nBy {name}"
                except Exception:
                    cleaned_text += f"\n\nBy group"
            sent = await send_with_retry(bot.send_message, **send_kwargs, text=cleaned_text)

            messageMap = await MessageMap.create(
                chat_id=event.chat_id,
                msg_id=event.id,
                sent_msg_id=sent.message_id,
                is_thread=bool(thread_id)
            )
            await OriginalMessage.create(text=event.text, message_map=messageMap)  # TODO: заменить на f"\n\nBy {name}"

        print("Сообщение отправлено!\n")

    except Exception as e:
        print(traceback.format_exc())
        with open('errors.txt', 'a', encoding='utf-8') as f:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            f.write(f'[{now}] Ошибка при отправке сообщения:\n')
            f.write(f'Target ID: {target_chat_id}\n')
            f.write(f'Thread ID: {thread_id}\n')
            f.write(f'Event: {event}\n')
            f.write(f'Ошибка: {str(e)}\n')
            f.write('Traceback:\n')
            f.write(traceback.format_exc())
            f.write('\n' + '=' * 80 + '\n')


def convert_telethon_markup_to_aiogram(markup: ReplyInlineMarkup) -> InlineKeyboardMarkup:
    keyboard = []

    for row in markup.rows:
        buttons = []
        for button in row.buttons:
            if isinstance(button, KeyboardButtonUrl):
                buttons.append(
                    InlineKeyboardButton(text=button.text, url=button.url)
                )
        keyboard.append(buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_filename_from_doc(doc):
    return next(
        (a.file_name for a in doc.attributes if isinstance(a, DocumentAttributeFilename)),
        "file" + get_extension(doc)
    )


def remove_lines_by_keywords(text: str, keywords: list) -> str:
    lines = text.strip().splitlines()
    filtered_lines = [line for line in lines if not any(keyword in line for keyword in keywords)]
    return "\n".join(filtered_lines)


async def send_with_retry(send_func, *args, **kwargs):
    try:
        return await send_func(*args, **kwargs)
    except TelegramBadRequest:
        kwargs["parse_mode"] = None
        return await send_func(*args, **kwargs)


async def _get_media_posts_in_group(chat, original_post, max_amp=10):
    if original_post.grouped_id is None:
        return [original_post] if original_post.media is not None else []

    search_ids = [i for i in range(original_post.id - max_amp, original_post.id + max_amp + 1)]
    posts = await client.get_messages(chat, ids=search_ids)
    media = []
    for post in posts:
        if post is not None and post.grouped_id == original_post.grouped_id and post.media is not None:
            media.append(post)
    return media


async def handle_media_message(event, media_group, send_kwargs, thread_id):
    message = event.message
    text = message.text or ""

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
                name = get_filename_from_doc(msg.media.document)
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
            sent = await send_with_retry(bot.send_photo, **send_kwargs,
                                         photo=BufferedInputFile(file, filename="photo.jpg"), caption=text)
        elif message.sticker:
            name = get_filename_from_doc(event.media.document)
            sent = await bot.send_sticker(**send_kwargs, sticker=BufferedInputFile(file, filename=name))
        elif message.video:
            sent = await send_with_retry(bot.send_video, **send_kwargs,
                                         video=BufferedInputFile(file, filename="video.mp4"), caption=text)
        elif message.voice:
            sent = await bot.send_voice(**send_kwargs, voice=BufferedInputFile(file, filename="voice.ogg"))
        elif message.audio:
            sent = await bot.send_audio(**send_kwargs, audio=BufferedInputFile(file, filename="audio.mp3"))
        elif message.document:
            name = get_filename_from_doc(event.media.document)
            sent = await send_with_retry(bot.send_document, **send_kwargs,
                                         document=BufferedInputFile(file, filename=name), caption=text)
        else:
            sent = await send_with_retry(bot.send_message, **send_kwargs, text=text)

    try:
        messageMap = await MessageMap.create(
            chat_id=event.chat_id,
            msg_id=event.id,
            sent_msg_id=sent.message_id,
            is_thread=bool(thread_id),
            has_media=True
            # media_group_ids=[msg.message_id for msg in sent]
        )
        await OriginalMessage.create(text=event.text, message_map=messageMap)

        print("Сообщение с картинкой отправлено!\n")
    except Exception as e:
        print("image", e)
        print("event: ", event)


async def get_monitored_channels():
    return await ForwardRule.all().distinct().values_list('source_channel', flat=True)


async def get_forward_targets(source_channel, thread_id=None):
    channel_rules = await ForwardRule.filter(
        source_channel=source_channel,
        thread_id=thread_id
    ).first()

    if channel_rules is None:
        return None

    if channel_rules.dest_thread is None:
        return [channel_rules.dest_channel]
    return [channel_rules.dest_channel, channel_rules.dest_thread]


async def get_keywords_to_remove():
    keywords = await KeywordToRemove.all().values_list('keyword', flat=True)
    return list(keywords)


async def get_keywords_to_skip():
    keywords = await KeywordToSkip.all().values_list('keyword', flat=True)
    return list(keywords)


async def get_channel_bypass_skip():
    channels = await ChannelBypassSkip.all().values_list('channel_id', flat=True)
    return list(channels)


async def get_thread_bypass_skip():
    threads = await ThreadBypassSkip.all().values_list('thread_id', flat=True)
    return list(threads)
