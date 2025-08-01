from models import ForwardRule
from utils import *


async def handle_message_delete(event):
    chat_id = event.chat_id
    if not await in_monitored_channels(chat_id):
        return

    fwd_rule = await ForwardRule.filter(chat_id=chat_id).first()  # TODO: Возможно изменить на thread=null в конфиге
    if not fwd_rule:
        return

    for deleted_id in event.deleted_ids:
        message_map = await get_message_map_safe(chat_id, deleted_id)
        if not message_map:
            continue

        updated_text = f"{message_map.orig_msg.text}\n\n❌ [УДАЛЕНО]"
        await edit_forwarded_message(
            fwd_rule.target_chat_id,
            message_map.target_msg_id,
            updated_text,
            message_map.has_media
        )
