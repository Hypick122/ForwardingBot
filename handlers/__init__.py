from .message_deleter import handle_message_delete
from .message_editor import handle_message_edit
from .message_forwarder import handle_message_forwarding
from . import commands

__all__ = (
    'handlers',
    'routers'
)

handlers = [
    handle_message_delete,
    handle_message_edit,
    handle_message_forwarding
]

routers = [
    commands.router
]
