from typing import Dict, List, Tuple, Union

from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = (
    'config',
    'TOPICS_CHAT_ID',
    'FORWARD_RULES',
    'KEYWORDS_TO_REMOVE',
    'KEYWORDS_TO_SKIP',
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
# TOPICS_CHAT_ID = -1002121900603  # Test

FORWARD_RULES: Dict[int, Union[
    List[Tuple[int, str]],
    Dict[int, List[Tuple[int, str]]]
]] = {
    # -1002119837460: [1881],  # Test
    -1002119837460: [-1002518956357],  # Test 2
    -1002270373322: [-1002632555419, 3],  # D Private
    -1002628565313: [-1002548734407],  # D Mexc Orders
    -1002508850717: [-1002650379204, 289],  # Favor
    -1002519569203: [-1002357512003, 34003],  # чат Фарова
    -1002506549679: [-1002566963522],  # Приватка REKT BOYS
    -1002164115278: {  # Finder
        #     255932: [-1002602282145, 2671],
        #     639209: [-1002602282145, 2671],
        #     799294: [-1002156956399],
        #     749282: [-1002503709125],
        #     799323: [-1002513750593],
        #     799326: [-1002622101781],
        #     799329: [-1002473347842, 55],
        #     822767: [50],
    },
    -1002408242605: {  # Furios
        9282: [-1002602282145, 2671],  # Коллы Подписчиков!
        4: [-1002527193117],  # 8%+ SHORT
        8978: [-1002505978486],  # 8%+ LONG
        42075: [-1002587120173],  # Big Jumps CEX Futures
        102560: [-1002590490169],  # Dex Jumps
        13: [-1002666514700],  # Статус: Депы/Выводы | Анонсы
    },
    -1002361161091: {  # Genesis
        2981: [-1002602282145, 2672],  # Community Calls
        1986: [-1002473347842, 55],  # LifeChange
        257775: [-1002697152513],  # HighSpread (DEX - Futures)
        976: [-1002684244383],  # Spread (DEX - Futures)
        257777: [-1002349398336],  # Spread (DEX - MEXC)
        # 309151: [], # Spread (Cross-Chain)
        65654: [-1002552070397],  # LowSpread (DEX - Futures)
        5: [-1002556157108],  # Spread (Listings)
        736: [-1002680618760],  # Spread (PreMarket)
        # 162298: [-1002357512003], # ?
        79323: [-1002340286874],  # Spread (CEX ALL)
        28935: [-1002213854723],  # Spread (DEX - Spot)
        17853: [-1002570238300],  # Spread (Funding)
        # 104656: [-1002682962170], # Manipulations (MEXC)
        63012: [-1002645526096],  # CEX Pumps&Dumps
        60756: [-1002560039323],  # DEX Dumps
        # 65243: [-1002643287474], # SKYNΞT (𝛽𝑒𝑡𝑎-𝓥𝑒𝑟𝑠𝑖𝑜𝑛)
        96958: [-1002622101781],  # AntiSpread (DEX - Futures)
        3: [-1002590335637],  # Notifications
        9: [98],  # Chat
    },
    -1002293398473: {  # ALL IN1 TRACKER
        3830: [-1002602282145, 2672],  # Коллы комьюнити
        679: [-1002473347842, 55],  # Finder Lifechange
        674: [-1002513750593],  # Finder High
        45795: [-1002682962170],  # Ежедневный сбор (листинга, разлоки и тд)
        13144: [-1002156956399],  # Kodak
        72301: [-1002503709125],  # Arty private
        5914: [-1002675596515],  # Parser Unlock
        72350: [-1002292004887],  # Ramar news
        597: [-1002474815715],  # Свиные уши
        596: [-1002643287474],  # Коля флипает
        35311: [-1002674130118],  # Crypto Angel (Maloletoff)
        56053: [-1002546283844],  # 77 щитпост
        13781: [-1002650379204, 289],  # AA private (favor)
        # 45155: [], # 01k alpha
    }
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
]
THREAD_ID_BYPASS_SKIP = [2671, 55, 50, 98]

config = Settings()
