from telethon.events import NewMessage, MessageEdited, MessageDeleted

from . import commands
from .message_deleter import handle_message_delete
from .message_editor import handle_message_edit
from .message_forwarder import handle_message_forwarding

__all__ = (
    'handlers',
    'routers'
)

handlers = [
    (handle_message_forwarding, NewMessage()),
    (handle_message_edit, MessageEdited()),
    (handle_message_delete, MessageDeleted())
]

routers = [
    commands.router
]
