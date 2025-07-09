import logging
import logging_config

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from telethon.sync import TelegramClient

__all__ = (
    'TOPICS_CHAT_ID',
    'config',
    'logger',
    'client',
    'bot',
    'dp'
)

load_dotenv()

TOPICS_CHAT_ID = -1002676817892


class Settings(BaseSettings):
    PHONE: str
    API_ID: SecretStr
    API_HASH: SecretStr
    SESSION_NAME: str
    BOT_TOKEN: SecretStr

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()

logger = logging.getLogger(__name__)

client = TelegramClient(
    config.SESSION_NAME,
    config.API_ID.get_secret_value(),
    config.API_HASH.get_secret_value(),
    system_version='4.16.30-vxCUSTOM'
)

bot = Bot(
    token=config.BOT_TOKEN.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
dp = Dispatcher(storage=MemoryStorage())
