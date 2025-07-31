from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = (
    'params',
    'ADMIN_ID'
)

load_dotenv()


class Settings(BaseSettings):
    PHONE: str
    API_ID: SecretStr
    API_HASH: SecretStr
    SESSION_NAME: str
    BOT_TOKEN: SecretStr

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


params = Settings()

ADMIN_ID = 668623130