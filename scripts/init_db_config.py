from pathlib import Path

import json5

from models import *

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"

FORWARD_RULES_PATH = CONFIG_DIR / "forward_rules.json5"
KEYWORDS_REMOVE_PATH = CONFIG_DIR / "keywords_to_remove.json5"
KEYWORDS_SKIP_PATH = CONFIG_DIR / "keywords_to_skip.json5"


async def init_config():
    await _init_keywords_to_remove()
    await _init_keywords_to_skip()
    await _init_forward_rules()


async def _init_keywords_to_remove():
    with open(KEYWORDS_REMOVE_PATH, "r", encoding="utf-8") as f:
        keywords = json5.load(f)

    for keyword in keywords:
        await KeywordToRemove.get_or_create(keyword=keyword)


async def _init_keywords_to_skip():
    with open(KEYWORDS_SKIP_PATH, "r", encoding="utf-8") as f:
        keywords = json5.load(f)

    for keyword in keywords:
        await KeywordToSkip.get_or_create(keyword=keyword)


async def _init_forward_rules():
    with open(FORWARD_RULES_PATH, "r", encoding="utf-8") as f:
        rules_raw = json5.load(f)

    for chat_id, data in rules_raw.items():
        for rule in data:
            await ForwardRule.get_or_create(
                chat_id=chat_id,
                thread_id=rule["thread_id"],
                target_chat_id=rule["target_chat_id"],
                skip=rule["skip"]
            )
