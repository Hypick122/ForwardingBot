import traceback

from aiogram.exceptions import TelegramBadRequest
from telethon import events
from tortoise.exceptions import DoesNotExist

from core import *
from core.utils import send_with_retry
from models import MessageMap


@client.on(events.MessageEdited())
async def handle_message_edit(event):
    if not isinstance(event, events.MessageEdited.Event):
        return

    chat_id = event.chat_id
    if chat_id not in await get_monitored_channels():
        return

    reply_to_top_id = None
    if event.reply_to:
        if event.reply_to.reply_to_top_id:
            reply_to_top_id = event.reply_to.reply_to_top_id
        elif event.reply_to.forum_topic:
            reply_to_top_id = event.reply_to.reply_to_msg_id

    if (reply_to_top_id and
            ((chat_id == -1002408242605 and reply_to_top_id != 9282) or
             (chat_id == -1002361161091 and reply_to_top_id not in [2981, 9]) or
             (chat_id == -1002293398473 and reply_to_top_id in [679, 674, 5914]))):
        return

    forward_targets = await get_forward_targets(chat_id, reply_to_top_id)
    if not forward_targets:
        return

    for target_id in forward_targets:
        target_chat_id = TOPICS_CHAT_ID if target_id > 0 else target_id
        thread_id = target_id if target_id > 0 else None
        try:
            message_map_id = await MessageMap.get(
                chat_id=event.chat_id,
                msg_id=event.id,
                is_thread=True if target_id > 0 else False
            ).prefetch_related('orig_msg')

            cleaned_text = remove_lines_by_keywords(event.text, await get_keywords_to_remove())
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

            if message_map_id.has_media:
                await send_with_retry(
                    bot.edit_message_caption,
                    chat_id=target_chat_id,
                    message_id=message_map_id.sent_msg_id,
                    caption=cleaned_text or ""
                )
            else:
                await send_with_retry(
                    bot.edit_message_text,
                    chat_id=target_chat_id,
                    message_id=message_map_id.sent_msg_id,
                    text=cleaned_text or "",
                    disable_web_page_preview=True
                )
        except DoesNotExist:
            continue
        except TelegramBadRequest as e:
            print("edit: message is not modified")
            if "message is not modified" not in str(e):
                raise
        except Exception:
            print("\nEDIT ERROR:")
            print("chat_id: ", chat_id)
            print("reply_to_top_id: ", reply_to_top_id)
            print("event: ", event)
            print("forward_targets: ", forward_targets)
            print(traceback.format_exc())
