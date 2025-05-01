# # from os import getenv
# #
# # from dotenv import load_dotenv
# # from telethon import TelegramClient, events
# #
# # load_dotenv)
# #
# # PHONE = getenv'PHONE')
# # API_ID = intgetenv'API_ID'))
# # API_HASH = getenv'API_HASH')
# # SESSION_NAME = getenv'SESSION_NAME')
# #
# # SOURCE_CHANNEL_ID = -1002119837460
# # DESTINATION_CHAT_ID = -1002121900603
# #
# # client = TelegramClientSESSION_NAME, API_ID, API_HASH, system_version='4.16.30-vxCUSTOM')
# #
# #
# # @client.onevents.NewMessagechats=SOURCE_CHANNEL_ID))
# # async def forward_messageevent):
# #     try:
# #         await client.forward_messagesDESTINATION_CHAT_ID, event.message)
# #         printf"Переслано сообщение: {event.text}")
# #     except Exception as e:
# #         printf"Ошибка: {e}")
# #
# #
# # async def main):
# #     await client.startPHONE)
# #     print"Бот запущен и слушает сообщения...")
# #     await client.run_until_disconnected)
# #
# #
# # if __name__ == '__main__':
# #     client.loop.run_until_completemain))
#
# import asyncio
# from os import getenv
#
# from aiogram import Bot
# from dotenv import load_dotenv
# from telethon import TelegramClient, events
#
# load_dotenv)
#
# PHONE = getenv'PHONE')
# API_ID = intgetenv'API_ID'))
# API_HASH = getenv'API_HASH')
# SESSION_NAME = getenv'SESSION_NAME')
# BOT_TOKEN = getenv'BOT_TOKEN')
#
# SOURCE_CHANNEL_ID = -1002119837460
# DESTINATION_CHAT_ID = -1002121900603
#
# bot = Bottoken=BOT_TOKEN)
# client = TelegramClientSESSION_NAME, API_ID, API_HASH, system_version='4.16.30-vxCUSTOM')
#
#
# @client.onevents.NewMessagechats=SOURCE_CHANNEL_ID))
# async def telethon_handlerevent):
#     try:
#         await bot.send_messageDESTINATION_CHAT_ID, event.text)
#         printf"Переслано: {event.text}")
#     except Exception as e:
#         printf"Ошибка: {e}")
#
#
# async def main):
#     await client.startPHONE)
#     print"Мониторинг запущен...")
#     await client.run_until_disconnected)
#
#
# if __name__ == "__main__":
#     asyncio.runmain))

# CHANNEL_TOPIC = {
#     2270373322: 3,
#     2270373321: 3,
#     2270373320: 1,
# }
# TOPIC_MAP = {
#     **CHANNEL_TOPIC
# }
#
# print[i for i in CHANNEL_TOPIC.keys)])

from typing import Dict, Tuple, Union, List




@client.on(events.NewMessage(chats=[
    -1002164115278,  # Finder
    -1002408242605,  # Furious
    -1002270373322,  # D Private
    -1002361161091,  # Genesis
    -1002508850717,  # favor
    # -1002119837460,  # test channel
]))
async def handler(event):
    if not isinstance(event, events.NewMessage.Event):
        return

    try:
        caption = event.message.message or ""
        markup = convert_telethon_markup_to_aiogram(event.reply_markup) if event.reply_markup else None

        thread_id_raw = None
        if event.peer_id.channel_id in ALL_CHANNEL_IDS:
            print("channel")
            thread_id_raw = event.peer_id.channel_id
        elif event.reply_to:
            thread_id_raw = event.reply_to.reply_to_top_id or event.reply_to.reply_to_msg_id

        thread_info = TOPIC_MAP.get(thread_id_raw)
        if not thread_info:
            return

        for topic_id in thread_info:
            dest_chat_id = CHAT_ID if topic_id >= 1 else topic_id
            dest_thread_id = topic_id if topic_id >= 1 else None
            if event.reply_to and dest_thread_id:
                reply_to_id = message_map.get(event.reply_to.reply_to_msg_id)
            elif event.reply_to and dest_thread_id is None:
                reply_to_id = channel_message_map.get(event.reply_to.reply_to_msg_id)
            else:
                reply_to_id = None

            if event.media and not isinstance(event.media, MessageMediaWebPage):
                file_bytes = await event.download_media(file=bytes)

                if isinstance(event.media, MessageMediaPhoto):
                    file_input = BufferedInputFile(file=file_bytes, filename="photo.jpg")
                    sent = await bot.send_photo(
                        chat_id=dest_chat_id,
                        message_thread_id=dest_thread_id,
                        photo=file_input,
                        caption=caption,
                        reply_to_message_id=reply_to_id,
                        reply_markup=markup,
                        has_spoiler=event.media.spoiler,
                        parse_mode="Markdown"
                    )

                elif isinstance(event.media, MessageMediaDocument):
                    doc = event.media.document
                    filename = get_filename_from_doc(doc)
                    if is_gif(doc) and not filename.endswith(".mp4"):
                        filename = "animation.mp4"
                    file_input = get_file_input(file_bytes, filename)

                    if is_sticker(doc):
                        sent = await send_with_retry(
                            bot.send_sticker,
                            chat_id=dest_chat_id,
                            message_thread_id=dest_thread_id,
                            sticker=file_input
                        )
                    elif is_gif(doc):
                        sent = await send_with_retry(
                            bot.send_animation,
                            chat_id=dest_chat_id,
                            message_thread_id=dest_thread_id,
                            animation=file_input,
                            caption=caption,
                            reply_to_message_id=reply_to_id,
                            reply_markup=markup,
                            has_spoiler=event.media.spoiler
                        )
                    elif event.media.video:
                        sent = await send_with_retry(
                            bot.send_video,
                            chat_id=dest_chat_id,
                            message_thread_id=dest_thread_id,
                            video=file_input,
                            caption=caption,
                            reply_to_message_id=reply_to_id,
                            reply_markup=markup,
                            has_spoiler=event.media.spoiler,
                            parse_mode="Markdown"
                        )
                    else:
                        sent = await send_with_retry(
                            bot.send_document,
                            chat_id=dest_chat_id,
                            message_thread_id=dest_thread_id,
                            document=file_input,
                            caption=caption,
                            reply_to_message_id=reply_to_id,
                            reply_markup=markup,
                            parse_mode="Markdown"
                        )

            elif event.text:
                if (any(keyword in event.text for keyword in KEYWORDS_TO_SKIP) and topic_id not in THREAD_ID_BYPASS_SKIP
                        or any(keyword in event.text for keyword in
                               KEYWORDS_TO_SKIP_FUNDING) and dest_chat_id == -1002570238300):
                    print(f"skip (Funding: {dest_chat_id == -1002570238300})\n")
                    return

                cleaned_text = remove_lines_by_keywords(event.text, KEYWORDS_TO_REMOVE)

                # if not markup and dest_chat_id == -1002570238300:
                #     markup = create_markup(cleaned_text)

                sent = await send_with_retry(
                    bot.send_message,
                    chat_id=dest_chat_id,
                    message_thread_id=dest_thread_id,
                    text=cleaned_text,
                    reply_to_message_id=reply_to_id,
                    reply_markup=markup,
                    disable_web_page_preview=True,
                    parse_mode="Markdown"
                )

            if event.peer_id.channel_id in ALL_CHANNEL_IDS:
                channel_message_map[event.id] = sent.message_id
                original_messages[event.id] = event.text
            elif dest_thread_id:
                message_map[event.id] = sent.message_id
            # print()

    except Exception:
        # print("dest_chat_id: ", dest_chat_id)
        # print("dest_thread_id: ", dest_thread_id)
        # print("reply_to_id: ", reply_to_id)
        print("event: ", event)
        print("ERROR: ", traceback.format_exc())