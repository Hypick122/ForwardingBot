from tortoise.exceptions import DoesNotExist

from models import *

__all__ = (
    'get_monitored_channels',
    'get_forward_targets',
    'get_keywords_to_remove',
    'get_keywords_to_skip',
    'get_bypass_skip',
    'safe_get_message_map'
)


async def get_monitored_channels():
    return await ForwardRule.all().distinct().values_list('chat_id', flat=True)


async def get_forward_targets(channel, thread_id=None) -> ForwardRule:
    return await ForwardRule.filter(chat_id=channel, thread_id=thread_id).first()


async def get_keywords_to_remove():
    return list(await KeywordToRemove.all().values_list('keyword', flat=True))


async def get_keywords_to_skip():
    return list(await KeywordToSkip.all().values_list('keyword', flat=True))


async def get_bypass_skip(chat_id, thread_id=None):
    forward_rule = await ForwardRule.filter(chat_id=chat_id, thread_id=thread_id).first()
    return forward_rule.skip


async def safe_get_message_map(chat_id, msg_id):
    try:
        return await MessageMap.get(chat_id=chat_id, msg_id=msg_id).prefetch_related('orig_msg')
    except DoesNotExist:
        return None
