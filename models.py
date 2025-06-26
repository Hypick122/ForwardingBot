from tortoise import fields
from tortoise.models import Model

__all__ = (
    'MessageMap',
    'OriginalMessage',
    'KeywordToRemove',
    'KeywordToSkip',
    'ChannelBypassSkip',
    'ThreadBypassSkip',
    'ForwardRule'
)


class MessageMap(Model):
    id = fields.IntField(pk=True)
    chat_id = fields.BigIntField()
    msg_id = fields.BigIntField()
    sent_msg_id = fields.BigIntField()
    is_thread = fields.BooleanField(default=False)
    has_media = fields.BooleanField(default=False)
    # media_group_ids = fields.JSONField(null=True)

    orig_msg: fields.ReverseRelation["OriginalMessage"]

    class Meta:
        table = 'messageMap'


class OriginalMessage(Model):
    id = fields.IntField(pk=True)
    text = fields.TextField()

    message_map: fields.OneToOneRelation[MessageMap] = fields.OneToOneField(
        "models.MessageMap", related_name="orig_msg", on_delete=fields.CASCADE
    )

    class Meta:
        table = 'originalMessage'


class KeywordToRemove(Model):
    id = fields.IntField(pk=True)
    keyword = fields.CharField(max_length=255, unique=True)

    class Meta:
        table = 'keywords_to_remove'


class KeywordToSkip(Model):
    id = fields.IntField(pk=True)
    keyword = fields.CharField(max_length=255, unique=True)

    class Meta:
        table = 'keywords_to_skip'


class ChannelBypassSkip(Model):
    id = fields.IntField(pk=True)
    channel_id = fields.BigIntField(unique=True)

    class Meta:
        table = 'channel_bypass_skip'


class ThreadBypassSkip(Model):
    id = fields.IntField(pk=True)
    thread_id = fields.BigIntField(unique=True)

    class Meta:
        table = 'thread_bypass_skip'


class ForwardRule(Model):
    id = fields.IntField(pk=True)
    source_channel = fields.BigIntField()
    thread_id = fields.BigIntField(null=True)
    dest_channel = fields.BigIntField()
    dest_thread = fields.BigIntField(null=True)

    class Meta:
        table = 'forward_rules'
        unique_together = (('source_channel', 'thread_id'),)
