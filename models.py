from tortoise import fields
from tortoise.models import Model

__all__ = (
    'MessageMap',
    'OriginalMessage',
)


class MessageMap(Model):
    id = fields.IntField(pk=True)
    msg_id = fields.IntField()
    sent_msg_id = fields.IntField()
    is_thread = fields.BooleanField(default=False)

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
