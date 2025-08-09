import asyncio
from pathlib import Path
from typing import Any

import json5

from config import logger
from models import *

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"

FORWARD_RULES_PATH = CONFIG_DIR / "forward_rules.json5"
KEYWORDS_REMOVE_PATH = CONFIG_DIR / "keywords_to_remove.json5"
KEYWORDS_SKIP_PATH = CONFIG_DIR / "keywords_to_skip.json5"


async def init_config():
    await asyncio.gather(
        _init_keywords(KEYWORDS_REMOVE_PATH, KeywordToRemove),
        _init_keywords(KEYWORDS_SKIP_PATH, KeywordToSkip),
        _init_forward_rules()
    )


def _load_json5(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json5.load(f)


async def _init_keywords(path: Path, model) -> None:
    keywords = _load_json5(path)
    if not keywords:
        return

    tasks = [
        model.get_or_create(keyword=kw)
        for kw in keywords
    ]
    await asyncio.gather(*tasks)
    logger.info(f"Загружено {len(tasks)} ключевых слов в {model.__name__}.")


def parse_target(targets_raw):
    targets = targets_raw if isinstance(targets_raw, list) else [targets_raw]
    result = [{
        'chat_id': t if isinstance(t, (int, str)) else t['chat_id'],
        'thread_id': None if isinstance(t, (int, str)) else t.get('thread_id')
    } for t in targets]

    return result


async def _init_forward_rules():
    rules_raw = _load_json5(FORWARD_RULES_PATH)

    tasks = []
    for chat_id, rules in rules_raw.items():
        for rule in rules:
            targets = parse_target(rule['target'])
            for target in targets:
                tasks.append(
                    ForwardRule.get_or_create(
                        chat_id=int(chat_id),
                        thread_id=rule.get("thread_id", None),
                        target_chat_id=target["chat_id"],
                        target_thread_id=target['thread_id'],
                        show_author=rule.get("show_author", False),
                        skip=rule.get("skip", True)
                    )
                )

    await asyncio.gather(*tasks)
    logger.info(f"Загружено {len(tasks)} правил пересылки.")
