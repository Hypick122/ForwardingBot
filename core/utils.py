import traceback
from datetime import datetime

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import ReplyInlineMarkup, KeyboardButtonUrl, DocumentAttributeFilename
from telethon.utils import get_extension
from tortoise.exceptions import DoesNotExist

from core.config import *
from core.loader import *

__all__ = (
    'connect_to_session',
    'send_message',
    'convert_telethon_markup_to_aiogram',
    'get_filename_from_doc',
    'remove_lines_by_keywords',
)

from models import MessageMap, OriginalMessage


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
                mapping = await MessageMap.get(
                    msg_id=event.reply_to.reply_to_msg_id,
                    is_thread=bool(thread_id)
                )
                send_kwargs["reply_to_message_id"] = mapping.sent_msg_id
            except DoesNotExist:
                pass

        if thread_id:
            send_kwargs["message_thread_id"] = thread_id

        if message.media:
            file = await event.download_media(file=bytes)

            if message.photo:
                await send_with_retry(bot.send_photo, **send_kwargs,
                                      photo=BufferedInputFile(file, filename="photo.jpg"), caption=text)
            elif message.sticker:
                name = get_filename_from_doc(event.media.document)
                await bot.send_sticker(**send_kwargs, sticker=BufferedInputFile(file, filename=name))
            # elif is_gif(doc): # TODO
            elif message.video:
                await send_with_retry(bot.send_video, **send_kwargs,
                                      video=BufferedInputFile(file, filename="video.mp4"), caption=text)
            elif message.voice:
                await bot.send_voice(**send_kwargs, voice=BufferedInputFile(file, filename="voice.ogg"))  # caption=text
            elif message.audio:
                await bot.send_audio(**send_kwargs, audio=BufferedInputFile(file, filename="audio.mp3"))  # caption=text
            elif message.document:
                name = get_filename_from_doc(event.media.document)
                await send_with_retry(bot.send_document, **send_kwargs, document=BufferedInputFile(file, filename=name),
                                      caption=text)
        else:
            if any(keyword in event.text for keyword in KEYWORDS_TO_SKIP) and thread_id not in THREAD_ID_BYPASS_SKIP:
                print("skip")
                print("any(keyword in event.text for keyword in KEYWORDS_TO_SKIP): ",
                      any(keyword in event.text for keyword in KEYWORDS_TO_SKIP))
                print("thread_id not in THREAD_ID_BYPASS_SKIP: ", thread_id not in THREAD_ID_BYPASS_SKIP)
                return

            send_kwargs["disable_web_page_preview"] = True
            send_kwargs["parse_mode"] = "Markdown"

            cleaned_text = remove_lines_by_keywords(text, KEYWORDS_TO_REMOVE)
            if target_chat_id == -1002357512003 or thread_id in [50, 98, 34003]:
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
                    cleaned_text += f"\n\nBy (ID) {event.from_id.user_id}"
            sent = await send_with_retry(bot.send_message, **send_kwargs, text=cleaned_text)

            messageMap = await MessageMap.create(
                msg_id=event.id,
                sent_msg_id=sent.message_id,
                is_thread=False if thread_id is None else True
            )
            await OriginalMessage.create(text=event.text, message_map=messageMap)  # TODO: заменить на f"\n\nBy {name}"

    except TelegramBadRequest as e:
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


# def create_markup(cleaned_text: str) -> InlineKeyboardMarkup:
#     contract_match = re.search(r"Контракт:\s*([A-Za-z0-9]{32,})", cleaned_text)
#     contract = contract_match.group(1) if contract_match else None
#
#     ticker_match = re.search(r"Монета:\s*([A-Z0-9]{2,})", cleaned_text)
#     ticker = ticker_match.group(1) if ticker_match else None
#
#     extra_buttons = []
#     if contract:
#         extra_buttons.append(InlineKeyboardButton(text="GMGN", url=f"https://gmgn.ai/sol/token/{contract}"))
#     if ticker:
#         extra_buttons.append(InlineKeyboardButton(text="MEXC", url=f"https://futures.mexc.com/exchange/{ticker}_USDT"))
#
#     # if markup:
#     #     markup.inline_keyboard.append(extra_buttons)
#     # if extra_buttons:
#     #     markup = InlineKeyboardMarkup(inline_keyboard=[extra_buttons])
#
#     return InlineKeyboardMarkup(inline_keyboard=[extra_buttons])


def get_filename_from_doc(doc):
    return next(
        (a.file_name for a in doc.attributes if isinstance(a, DocumentAttributeFilename)),
        "file" + get_extension(doc)
    )


# def get_file_input(event_media, filename="file.bin"):
#     return BufferedInputFile(file=event_media, filename=filename)
#
#
# def is_gif(doc):
#     return any(isinstance(attr, DocumentAttributeAnimated) for attr in doc.attributes)
#
#
# def is_sticker(doc):
#     return any(isinstance(attr, DocumentAttributeSticker) for attr in doc.attributes)


def remove_lines_by_keywords(text: str, keywords: list) -> str:
    lines = text.strip().splitlines()
    filtered_lines = [line for line in lines if not any(keyword in line for keyword in keywords)]
    return "\n".join(filtered_lines)


# def safe_caption(caption: str) -> str:
#     lines = caption.splitlines()
#     safe_lines = []
#
#     for line in lines:
#         if re.match(r'https?://', line.strip()):
#             safe_lines.append(line)
#         else:
#             line = line.replace('\\', '\\\\')
#             line = re.sub(r'(?<!\\)([*`_])(?=\S)(.*?)(?<=\S)\1', r'\1\2\1', line)
#             line = re.sub(r'(?<!\\)([~|{}.!])', r'\\\1', line)
#             safe_lines.append(line)
#
#     return "\n".join(safe_lines)

async def send_with_retry(send_func, *args, **kwargs):
    try:
        return await send_func(*args, **kwargs)
    except TelegramBadRequest:
        kwargs["parse_mode"] = 'HTML'
        text = kwargs.get("caption") or kwargs.get("text")

        if text and len(text) > 4095:
            results = []

            for i in range(0, len(text), 4095):
                chunk = text[i:i + 4095]

                send_kwargs = dict(kwargs)

                if i > 0:
                    send_kwargs.pop("photo", None)
                    send_kwargs.pop("document", None)
                    send_kwargs.pop("video", None)

                if "caption" in send_kwargs:
                    send_kwargs["caption"] = chunk
                else:
                    send_kwargs["text"] = chunk

                result = await send_func(*args, **send_kwargs)
                results.append(result)

            # return results if len(results) > 1 else results[0]
            return results[-1]

        return await send_func(*args, **kwargs)
