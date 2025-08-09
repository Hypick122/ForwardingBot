import re

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity
from telethon.events import NewMessage
from telethon.tl.types import MessageEntityBold, MessageEntityItalic, MessageEntityTextUrl, MessageEntityUrl, \
    MessageEntityCode, MessageEntityPre, MessageEntityMention, MessageEntityHashtag, MessageEntityCashtag, \
    MessageEntityMentionName, MessageEntityUnderline, MessageEntityStrike, MessageEntityBotCommand, MessageEntityPhone, \
    MessageEntityEmail, ReplyInlineMarkup, KeyboardButtonUrl, User, Channel

from config import bot, logger
from models import *

__all__ = (
    'build_code_entities',
    'telethon_entities_to_aiogram',
    'parse_exchange_links',
    'parse_okx_link',
    'telethon_markup_to_aiogram',
    'remove_keywords_lines',
    'get_thread_id',
    'add_author',
    'edit_forwarded_message',
)


def build_code_entities(text: str, tickers: list[str]) -> list[MessageEntity]:
    entities = []
    for ticker in tickers:
        start = 0
        while True:
            pos = text.find(ticker, start)
            if pos == -1:
                break
            entities.append(MessageEntity(type="code", offset=pos, length=len(ticker)))
            start = pos + len(ticker)
    return entities


def telethon_entities_to_aiogram(entities):
    aiogram_entities = []

    for entity in entities or []:
        kwargs = {
            "offset": entity.offset,
            "length": entity.length,
        }

        if isinstance(entity, MessageEntityBold):
            kwargs["type"] = "bold"
        elif isinstance(entity, MessageEntityItalic):
            kwargs["type"] = "italic"
        elif isinstance(entity, MessageEntityCode):
            kwargs["type"] = "code"
        elif isinstance(entity, MessageEntityPre):
            kwargs["type"] = "pre"
        elif isinstance(entity, MessageEntityUnderline):
            kwargs["type"] = "underline"
        elif isinstance(entity, MessageEntityStrike):
            kwargs["type"] = "strikethrough"
        elif isinstance(entity, MessageEntityUrl):
            kwargs["type"] = "url"
        elif isinstance(entity, MessageEntityTextUrl):
            kwargs["type"] = "text_link"
            kwargs["url"] = entity.url.replace("/uk/", "/ru/").replace("/uk-UA/", "/ru-RU/")
        elif isinstance(entity, MessageEntityMention):
            kwargs["type"] = "mention"
        elif isinstance(entity, MessageEntityHashtag):
            kwargs["type"] = "hashtag"
        elif isinstance(entity, MessageEntityCashtag):
            kwargs["type"] = "cashtag"
        elif isinstance(entity, MessageEntityMentionName):
            kwargs["type"] = "text_mention"
            kwargs["user"] = entity.user
        elif isinstance(entity, MessageEntityBotCommand):
            kwargs["type"] = "bot_command"
        elif isinstance(entity, MessageEntityPhone):
            kwargs["type"] = "phone_number"
        elif isinstance(entity, MessageEntityEmail):
            kwargs["type"] = "email"
        else:
            continue

        aiogram_entities.append(MessageEntity(**kwargs))

    return aiogram_entities


def telethon_markup_to_aiogram(markup: ReplyInlineMarkup) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=btn.text, url=btn.url)
         for btn in row.buttons if isinstance(btn, KeyboardButtonUrl)]
        for row in markup.rows
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def parse_exchange_links(text: str):
    patterns = {
        'MEXC': {
            'spot': r"(?<!futures\.)mexc\.com/.*?exchange/([A-Z0-9_]+)",
            'futures': r"futures.mexc\.com/.*?exchange/([A-Z0-9_]+)",
        },
        'GATE.IO': {
            'spot': r"gate\.(?:io|com)/.*?trade/([A-Z0-9_]+)",
            'futures': r"gate\.(?:io|com)/.*?futures(?:_trade)?/USDT/([A-Z0-9_]+)"
        },
        'BYBIT': {
            'spot': r"bybit\.com/.*?spot/([A-Z0-9_/-]+)",
            'futures': r"bybit\.com/.*?usdt/([A-Z0-9_]+)"
        },
        'BITGET': {
            'spot': r"bitget\.com/.*?spot/([A-Z0-9_]+)",
            'futures': r"bitget\.com/.*?futures/usdt/([A-Z0-9_]+)"
        },
        'KUCOIN': {
            'spot': r"kucoin\.com/.*?trade/([A-Z0-9_-]+)",
            'futures': r"kucoin\.com/.*?futures/([A-Z0-9_-]+)"
        },
        'BINGX': {
            'spot': r"bingx\.com/.*?spot/([A-Z0-9_-]+)",
            'futures': r"bingx\.com/.*?(?:perpetual|futures/forward)/([A-Z0-9_-]+)"
        }
    }

    results = []

    for exch, regex_dict in patterns.items():
        for trade_type, regex in regex_dict.items():
            matches = re.findall(regex, text, re.IGNORECASE)
            for m in matches:
                ticker = re.sub(r'[_/-]', '', m.upper())  # убираем _, -, /
                if trade_type == 'futures':
                    ticker += '.p'
                results.append(f"{exch}:{ticker}")

    return results


def parse_okx_link(text):
    NETWORK_MAP = {
        'sol': 'solana',
        'eth': 'ethereum',
        'erc20': 'ethereum',
        'ethereum': 'ethereum',
        'bsc': 'bsc',
        'binance': 'bsc',
        'solana': 'solana',
        'sui': 'sui',
        'arbitrum': 'arbitrum-one',
        'avalanche': 'avalanche',
    }
    sui_contract_pattern = r'(0x[a-fA-F0-9]{64}::[a-zA-Z0-9_]+::[a-zA-Z0-9_]+)'
    general_contract_pattern = r'(0x[a-fA-F0-9]{40}|[a-zA-Z0-9]{30,64})'

    gmgn_pattern = rf'https?://(?:www\.)?gmgn\.ai/([^/]+)/token/({sui_contract_pattern}|{general_contract_pattern})'

    match = re.search(gmgn_pattern, text)
    if match:
        network_raw = match.group(1).lower()
        contract = match.group(2)
        network = NETWORK_MAP.get(network_raw, network_raw)
        return f"https://web3.okx.com/ru/token/{network}/{contract}"

    sui_in_text = re.search(r'(0x[a-fA-F0-9]{64}::[a-zA-Z0-9_]+::[a-zA-Z0-9_]+)', text)
    if sui_in_text:
        contract = sui_in_text.group(1)
        return f"https://web3.okx.com/ru/token/sui/{contract}"

    contract_match = re.search(general_contract_pattern, text)
    if contract_match:
        contract = contract_match.group(1)
        text_lower = text.lower()

        network_match = re.search(
            r'(bsc|erc20|ethereum|solana|sui|arbitrum|avalanche)[^\n\r:]*[:\s]+\s*' + re.escape(contract.lower()),
            text_lower)
        if network_match:
            network_raw = network_match.group(1)
        else:
            if 'erc20' in text_lower or 'ethereum' in text_lower or ' eth ' in text_lower:
                network_raw = 'ethereum'
            elif 'bsc' in text_lower or 'binance' in text_lower:
                network_raw = 'bsc'
            elif 'solana' in text_lower or ' sol ' in text_lower:
                network_raw = 'solana'
            elif 'sui' in text_lower:
                network_raw = 'sui'
            elif 'arbitrum' in text_lower:
                network_raw = 'arbitrum'
            elif 'avalanche' in text_lower:
                network_raw = 'avalanche'
            else:
                network_raw = 'ethereum'

        network = NETWORK_MAP.get(network_raw, network_raw)
        return f"https://web3.okx.com/ru/token/{network}/{contract}"

    return None


def get_thread_id(event: NewMessage.Event) -> int | None:
    if event.reply_to and event.reply_to.reply_to_top_id:
        return event.reply_to.reply_to_top_id
    elif event.reply_to and event.reply_to.forum_topic:
        return event.reply_to.reply_to_msg_id
    elif event.is_group and event.is_channel:  # default topic
        return 1

    return None


def remove_keywords_lines(text: str, keywords: list[str]) -> str:
    return "\n".join(
        line for line in text.strip().splitlines()
        if not any(kw in line for kw in keywords)
    )


def display_id(obj):
    return f"@{getattr(obj, 'username', None)}" if getattr(obj, "username", None) else f"ID {obj.id}"


async def add_author(event, fwd_rule: ForwardRule, text: str) -> str:
    if not fwd_rule.show_author:
        return text

    try:
        sender = await event.get_sender()
    except Exception as e:
        logger.error("sender error: ", e)
        return text

    if isinstance(sender, User):
        if sender.bot:
            return f"{text}\n\nBy bot {display_id(sender)}"
        else:
            first_name = sender.first_name or ""
            last_name = sender.last_name or ""
            username = sender.username or (sender.usernames[0].username if sender.usernames else "")
            full_name = f"{first_name} {last_name} {'(@' + username + ')' if username else ''}".strip()
            if not username:
                full_name = f" {first_name} {last_name} (ID: {sender.id})"

            return f"{text}\nBy {full_name}"
    elif isinstance(sender, Channel):
        return f"{text}\nBy channel {display_id(sender)}"
    else:
        return text


async def edit_forwarded_message(target_chat_id: int, target_msg_id: int, text: str, has_media: bool):
    if has_media:
        await bot.edit_message_caption(chat_id=target_chat_id, message_id=target_msg_id, caption=text)
    else:
        await bot.edit_message_text(chat_id=target_chat_id, message_id=target_msg_id, text=text,
                                    disable_web_page_preview=True)
