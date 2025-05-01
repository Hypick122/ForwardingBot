from typing import Dict, List, Tuple, Union

from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = (
    'config',
    'TOPICS_CHAT_ID',
    'FORWARD_RULES',
    'ALLOWED_TOPICS',
    'KEYWORDS_TO_REMOVE',
    'KEYWORDS_TO_SKIP',
    'KEYWORDS_TO_SKIP_FUNDING',
    'THREAD_ID_BYPASS_SKIP',
)

load_dotenv()


class Settings(BaseSettings):
    PHONE: str
    API_ID: SecretStr
    API_HASH: SecretStr
    SESSION_NAME: str
    BOT_TOKEN: SecretStr

    model_config = SettingsConfigDict(env_file='../.env', env_file_encoding='utf-8')


TOPICS_CHAT_ID = -1002676817892
# TOPICS_CHAT_ID = -1002121900603

FORWARD_RULES: Dict[int, Union[
    List[Tuple[int, str]],
    Dict[int, List[Tuple[int, str]]]
]] = {
    # -1002119837460: [1881],
    -1002519569203: [-1002357512003, 34003],  # чат Фарова
    -1002270373322: [-1002632555419, 3],  # D Private
    -1002508850717: [-1002650379204, 289],  # Favor
    -1002164115278: {  # Finder
        255932: [-1002602282145, 2671],
        639209: [-1002602282145, 2671],
        799294: [-1002156956399],
        749282: [-1002503709125],
        799323: [-1002513750593],
        799326: [-1002622101781],
        799329: [-1002473347842, 55],
        822767: [50],
    },
    -1002408242605: {  # Furios
        9282: [-1002602282145, 2671],
        4: [-1002527193117],
        8978: [-1002505978486],
        42075: [-1002587120173],
        102560: [-1002590490169],
        13: [-1002666514700],
    },
    -1002361161091: {  # Genesis
        2981: [-1002602282145, 2672],
        1986: [-1002473347842, 55],
        976: [-1002684244383],
        257775: [-1002697152513],
        65654: [-1002552070397],
        5: [-1002556157108],
        736: [-1002680618760],
        162298: [-1002357512003],
        79323: [-1002340286874],
        28935: [-1002213854723],
        17853: [-1002570238300],
        104656: [-1002682962170],
        63012: [-1002645526096],
        60756: [-1002560039323],
        65243: [-1002643287474],
        3: [-1002590335637],
        9: [98],
        257777: [-1002349398336]
    },
}

ALLOWED_TOPICS: Dict[int, list[int]] = {
    -1002164115278: [  # Finder
        255932, 639209, 799294,
        749282, 799323, 799326,
        799329, 822767
    ],
    -1002408242605: [  # Furios
        9282, 4, 8978,
        42075, 102560, 13
    ],
    -1002361161091: [  # Genesis
        2981, 1986, 976,
        257775, 65654, 5,
        736, 162298, 79323,
        28935, 17853, 104656,
        63012, 60756, 65243,
        3, 9, 257777
    ],
}

KEYWORDS_TO_REMOVE = [
    "https://t.me/send?start=SBdLEPQwnj-BkwNzEy",
    "Main Channel",
    "genesis-arbitrage.gitbook.io",
    "Twitter",
    "https://t.me/+lR4kw7umxL82MDQy",
    "0xB81319806E8B00b893a5BD420Ef299D15DE86BCA",
    "Created by __SkyNet__",
    " All spreads, graphs"
]
KEYWORDS_TO_SKIP = [
    "ONON",
    "Сигнал в ",
    "LifeChange Pump",
    "Potential Pump",
    "Открыть на OurBit Futures",
    "DOGEAI",
    "9UYAYvVS2cZ3BndbsoG1ScJbjfwyEPGxjE79hh5ipump"
]
KEYWORDS_TO_SKIP_FUNDING = [
    "HTX",
    "BingX",
    "Bitget",
    "Hyper"
]

# MAX_FILE_SIZE = 5 * 1024 * 1024
THREAD_ID_BYPASS_SKIP = [2671, 55, 50, 98]

config = Settings()
