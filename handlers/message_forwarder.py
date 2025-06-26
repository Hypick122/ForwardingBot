from telethon import events

from core import *


@client.on(events.NewMessage())
async def handle_message_forwarding(event):
    if not isinstance(event, events.NewMessage.Event):
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

    forward_targets = await get_forward_targets(chat_id, reply_to_top_id)
    if not forward_targets:
        return

    print("event: ", event)
    print("forward_targets", forward_targets)
    # print()

    for target_id in forward_targets:
        target_chat_id = TOPICS_CHAT_ID if target_id > 0 else target_id
        thread_id = target_id if target_id > 0 else None

        await send_message(target_chat_id, event, thread_id=thread_id)
