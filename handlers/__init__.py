from message_deleter import handle_message_delete
from message_editor import handle_message_edit
from message_forwarder import handle_message_forwarding

__all__ = (
    'handlers',
)

handlers = [
    handle_message_delete,
    handle_message_edit,
    handle_message_forwarding,
]
