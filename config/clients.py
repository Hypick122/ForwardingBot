from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from telethon.sync import TelegramClient

from config.settings import params

__all__ = (
    'client',
    'bot',
    'dp'
)

client = TelegramClient(
    params.SESSION_NAME,
    params.API_ID.get_secret_value(),
    params.API_HASH.get_secret_value(),
    system_version='4.16.30-vxCUSTOM'
)

bot = Bot(
    token=params.BOT_TOKEN.get_secret_value(),
    default=DefaultBotProperties(parse_mode=None)
)
dp = Dispatcher(storage=MemoryStorage())
