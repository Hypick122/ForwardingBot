from tortoise.exceptions import DoesNotExist

from models import *

__all__ = (
    'get_forward_rule',
    'get_skip_flag',
    'get_removal_keywords',
    'check_skip_keywords',
    'get_message_map_safe'
)


async def get_forward_rule(chat_id: int, thread_id: int | None = None) -> ForwardRule | None:
    return await ForwardRule.filter(chat_id=chat_id, thread_id=thread_id).first()


async def get_skip_flag(chat_id: int, thread_id: int | None = None) -> bool:
    forward_rule = await ForwardRule.filter(chat_id=chat_id, thread_id=thread_id).first()
    return forward_rule.skip


async def get_removal_keywords() -> list[str]:
    return list(await KeywordToRemove.all().values_list('keyword', flat=True))


async def check_skip_keywords(text: str) -> list[str]:
    skip_keywords = list(await KeywordToSkip.all().values_list('keyword', flat=True))
    return any(keyword.lower() in text.lower() for keyword in skip_keywords)


async def get_message_map_safe(chat_id: int, msg_id: int) -> MessageMap | None:
    try:
        return await MessageMap.get(chat_id=chat_id, msg_id=msg_id).prefetch_related('orig_msg')
    except DoesNotExist:
        return None
