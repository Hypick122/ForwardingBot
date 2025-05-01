from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from telethon.sync import TelegramClient
from tortoise import Tortoise

from core import config

__all__ = (
    'init_db',
    'client',
    'bot',
    'dp'
)


# Инициализация БД
async def init_db() -> None:
    print("init DB")
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['models']}
    )
    await Tortoise.generate_schemas()


client = TelegramClient(
    config.SESSION_NAME,
    config.API_ID.get_secret_value(),
    config.API_HASH.get_secret_value(),
    system_version='4.16.30-vxCUSTOM'
)

bot = Bot(
    token=config.BOT_TOKEN.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())
