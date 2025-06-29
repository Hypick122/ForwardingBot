from aiogram import Router, F, types
from aiogram.filters import Command

from models import *
from utils import *

router = Router()


@router.message(Command("config"))
@router.message(F.text.lower().split()[0] == 'config')
async def config_cmd(message: types.Message) -> None:
    help_text = (
        "🛠 <b>Настройка фильтров и правил пересылки:</b>\n\n"
        "<code>/keyremove</code> — ключевые слова для удаления\n"
        "<code>/keyskip</code> — ключевые слова для пропуска\n"
        "<code>/skip</code> — правила пересылки\n\n"
        "📌 Пример: <code>/keyskip ONON</code>"
    )

    await message.answer(help_text, parse_mode="HTML")

    config_parts = []

    keywords_to_remove = await get_keywords_to_remove()
    config_parts.append("🔴 <b>KeywordToRemove:</b>")
    config_parts.extend([f"  • <code>{item}</code>" for item in keywords_to_remove])

    keywords_to_skip = await get_keywords_to_skip()
    config_parts.append("\n🟡 <b>KeywordToSkip:</b>")
    config_parts.extend([f"  • <code>{item}</code>" for item in keywords_to_skip])

    forward_rules = await ForwardRule.all()
    config_parts.append("\n🟢 <b>ForwardRule (✅ - to skip):</b>")

    for rule in forward_rules:
        source = f"{rule.chat_id}"
        if rule.thread_id is not None:
            source += f", {rule.thread_id}"

        target = f"{rule.target_chat_id}"
        if rule.target_thread_id is not None:
            target += f", {rule.target_thread_id}"

        skip_icon = "✅" if rule.skip else "❌"
        rule_info = f"  • [{rule.id}] {source} → {target} [{skip_icon}]"
        config_parts.append(rule_info)

    await message.answer("\n".join(config_parts), disable_web_page_preview=True, parse_mode="HTML")


@router.message(Command("keyremove"))
@router.message(F.text.lower().split()[0] == 'keyremove')
async def key_remove_cmd(message: types.Message) -> None:
    if len(message.text.split()) < 2:
        return

    keyword = message.text.split()[1]
    exists = await KeywordToRemove.filter(keyword=keyword).first()
    if exists:
        await exists.delete()
        await message.answer(f"❌ Ключевое слово {keyword} удалено из KEYWORDS_TO_REMOVE")
    else:
        await KeywordToRemove.create(keyword=keyword)
        await message.answer(f"✅ Ключевое слово {keyword} добавлено в KEYWORDS_TO_REMOVE")


@router.message(Command("keyskip"))
@router.message(F.text.lower().split()[0] == 'keyskip')
async def key_skip_cmd(message: types.Message) -> None:
    if len(message.text.split()) < 2:
        return

    keyword = message.text.split()[1]
    exists = await KeywordToSkip.filter(keyword=keyword).first()
    if exists:
        await exists.delete()
        await message.answer(f"❌ Ключевое слово {keyword} удалено из KEYWORDS_TO_SKIP")
    else:
        await KeywordToSkip.create(keyword=keyword)
        await message.answer(f"✅ Ключевое слово {keyword} добавлено в KEYWORDS_TO_SKIP")


@router.message(Command("exit"))
async def exit_cmd() -> None:
    exit("Завершения работы бота")
