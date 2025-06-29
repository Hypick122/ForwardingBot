from models import *


async def init_config():
    keywords_to_remove = [
        "https://t.me/send?start=SBdLEPQwnj-BkwNzEy",
        "Main Channel",
        "genesis-arbitrage.gitbook.io",
        "Twitter",
        "https://t.me/+lR4kw7umxL82MDQy",
        "0xB81319806E8B00b893a5BD420Ef299D15DE86BCA",
        "Created by __SkyNet__",
        "All spreads, graphs"
    ]
    for keyword in keywords_to_remove:
        await KeywordToRemove.get_or_create(keyword=keyword)

    keywords_to_skip = [
        "ONON",
        "Сигнал в ",
        "LifeChange Pump",
        "Potential Pump",
        "Открыть на OurBit Futures",
        "LBank",
        # СНГ бан
        "USELESS",
        "Dz9mQ9NzkBcCsuGPFJ3r1bS4wgqKMHBPiVuniW8Mbonk",
        "JAGER",
        "0x74836cC0E821A6bE18e407E6388E430B689C66e9",
        "RATO",
        "0xf816507E690f5Aa4E29d164885EB5fa7a5627860",
        "TIBBIR",
        "0xA4A2E2ca3fBfE21aed83471D28b6f65A233C6e00",
        "GOONC",
        "ENfpbQUM5xAnNP8ecyEQGFJ6KwbuPjMwv7ZjR29cDuAb",
        "BUZZ",
        "9DHe3pycTuymFk4H4bbPoAJ4hQrr2kaLDF6J6aAKpump",
        "DOGINME",
        "0x6921B130D297cc43754afba22e5EAc0FBf8Db75b",
        "KEKIUS",
        "0x26E550AC11B26f78A04489d5F20f24E3559f7Dd9",
        "MOONPIG",
        "Ai3eKAWjzKMV8wRwd41nVP83yqfbAVJykhvJVPxspump"
    ]
    for keyword in keywords_to_skip:
        await KeywordToSkip.get_or_create(keyword=keyword)

    channel_ids = [-1002508850717, -1002519569203, -1002506549679]
    thread_ids = [9282, 13, 2981, 1986, 3, 9, 3830, 45795, 13144, 72301, 5914, 72350, 597, 596, 35311, 56053, 13781]

    forward_rules_data = {
        -1002119837460: [-1002518956357],  # Test 2
        -1002508850717: [-1002650379204, 289],  # Favor
        -1002519569203: [-1002357512003, 34003],  # чат Фарова
        -1002506549679: [-1002566963522],  # Приватка REKT BOYS
        -1002408242605: {  # Furios
            9282: [-1002602282145, 2671],  # Коллы Подписчиков!
            4: [-1002527193117],  # 8%+ SHORT
            8978: [-1002505978486],  # 8%+ LONG
            42075: [-1002587120173],  # Big Jumps CEX Futures
            # 102560: [-1002590490169],  # Dex Jumps
            13: [-1002666514700],  # Статус: Депы/Выводы | Анонсы
        },
        -1002361161091: {  # Genesis
            2981: [-1002602282145, 2671],  # Community Calls
            1986: [-1002473347842, 55],  # LifeChange
            257775: [-1002697152513],  # HighSpread (DEX - Futures)
            366252: [-1002632555419],  # Spread (CEX-CEX)
            976: [-1002684244383],  # Spread (DEX - Futures)
            257777: [-1002349398336],  # Spread (DEX - MEXC)
            309151: [-1002548734407],  # Spread (Cross-Chain)
            65654: [-1002552070397],  # LowSpread (DEX - Futures)
            5: [-1002556157108],  # Spread (Listings)
            736: [-1002680618760],  # Spread (PreMarket)
            # 162298: [-1002357512003], # ?
            79323: [-1002340286874],  # Spread (CEX ALL)
            28935: [-1002213854723],  # Spread (DEX - Spot)
            17853: [-1002570238300],  # Spread (Funding)
            # 104656: [-1002682962170], # Manipulations (MEXC)
            # 63012: [-1002645526096],  # CEX Pumps&Dumps
            # 60756: [-1002560039323],  # DEX Dumps
            # 65243: [-1002643287474], # SKYNΞT (𝛽𝑒𝑡𝑎-𝓥𝑒𝑟𝑠𝑖𝑜𝑛)
            96958: [-1002622101781],  # AntiSpread (DEX - Futures)
            3: [-1002590335637],  # Notifications
            9: [98],  # Chat
        },
        -1002293398473: {  # ALL IN1 TRACKER
            3830: [-1002602282145, 2671],  # Коллы комьюнити
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

    for source_channel, rules in forward_rules_data.items():

        if isinstance(rules, list):
            dest_channel = rules[0]
            dest_thread = rules[1] if len(rules) > 1 else None
            await ForwardRule.get_or_create(
                chat_id=source_channel,
                thread_id=None,
                target_chat_id=dest_channel,
                target_thread_id=dest_thread,
                skip=False if source_channel in channel_ids else True,
            )
        elif isinstance(rules, dict):
            for thread_id, dest in rules.items():

                if dest:
                    dest_channel = dest[0]
                    dest_thread = dest[1] if len(dest) > 1 else None
                    await ForwardRule.get_or_create(
                        chat_id=source_channel,
                        thread_id=thread_id,
                        target_chat_id=dest_channel,
                        target_thread_id=dest_thread,
                        skip=False if thread_id in thread_ids else True,
                    )
