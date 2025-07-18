import logging
import logging.config

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

TOPICS_CHAT_ID = -1002676817892

load_dotenv()

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        },
        'advanced': {
            'format': '%(asctime)s %(name)s:%(levelname)s:%(message)s'
        }
    },
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'level': 'INFO',
            'formatter': 'standard'
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'WARNING',
            'formatter': 'advanced',
            'filename': 'app.log',
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        '': {
            'handlers': ['stdout', 'file'],
            'level': 'INFO'
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    PHONE: str
    API_ID: SecretStr
    API_HASH: SecretStr
    SESSION_NAME: str
    BOT_TOKEN: SecretStr

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()

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
