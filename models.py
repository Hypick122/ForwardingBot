from tortoise import fields
from tortoise.models import Model

__all__ = (
    'MessageMap',
    'OriginalMessage',
    'KeywordToRemove',
    'KeywordToSkip',
    'ForwardRule'
)


class MessageMap(Model):
    id = fields.IntField(pk=True)
    chat_id = fields.BigIntField()
    msg_id = fields.BigIntField()
    target_msg_id = fields.BigIntField()
    has_media = fields.BooleanField(default=False)
    # media_group_ids = fields.JSONField(null=True)

    orig_msg: fields.ReverseRelation["OriginalMessage"]

    class Meta:
        table = 'message_map'


class OriginalMessage(Model):
    id = fields.IntField(pk=True)
    text = fields.TextField()

    message_map: fields.OneToOneRelation[MessageMap] = fields.OneToOneField(
        "models.MessageMap", related_name="orig_msg", on_delete=fields.CASCADE
    )

    class Meta:
        table = 'original_message'


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


class ForwardRule(Model):
    id = fields.IntField(pk=True)
    chat_id = fields.BigIntField()
    thread_id = fields.BigIntField(null=True)
    target_chat_id = fields.BigIntField()
    target_thread_id = fields.BigIntField(null=True)

    show_author = fields.BooleanField(default=True)
    skip = fields.BooleanField(default=True)

    class Meta:
        table = 'forward_rules'
        unique_together = (('chat_id', 'thread_id'),)
