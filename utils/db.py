from tortoise.exceptions import DoesNotExist

from models import *

__all__ = (
    'in_monitored_channels',
    'get_forward_rule',
    'get_skip_flag',
    'get_removal_keywords',
    'get_skip_keywords',
    'get_message_map_safe'
)


async def in_monitored_channels(chat_id: int) -> bool:
    return chat_id in await ForwardRule.all().distinct().values_list('chat_id', flat=True)


async def get_forward_rule(chat_id: int, thread_id: int | None = None) -> ForwardRule | None:
    return await ForwardRule.filter(chat_id=chat_id, thread_id=thread_id).first()


async def get_skip_flag(chat_id: int, thread_id: int | None = None) -> bool:
    forward_rule = await ForwardRule.filter(chat_id=chat_id, thread_id=thread_id).first()
    return forward_rule.skip


async def get_removal_keywords() -> list[str]:
    return list(await KeywordToRemove.all().values_list('keyword', flat=True))


async def get_skip_keywords() -> list[str]:
    return list(await KeywordToSkip.all().values_list('keyword', flat=True))


async def get_message_map_safe(chat_id: int, msg_id: int) -> MessageMap | None:
    try:
        return await MessageMap.get(chat_id=chat_id, msg_id=msg_id).prefetch_related('orig_msg')
    except DoesNotExist:
        return None
