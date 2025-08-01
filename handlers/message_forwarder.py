from utils import *


async def handle_message_forwarding(event):
    chat_id = event.chat_id
    if not await in_monitored_channels(chat_id):
        return

    thread_id = get_thread_id(event)
    fwd_rule = await get_forward_rule(chat_id, thread_id)
    if not fwd_rule:
        return

    is_skip = await get_skip_flag(chat_id, thread_id)
    if any(keyword in event.text for keyword in await get_skip_keywords()) and is_skip:
        return

    await send_message(event, fwd_rule.target_chat_id)
