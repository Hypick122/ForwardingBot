from aiogram import Router, F, types
from aiogram.filters import Command

from config import params
from models import *
from utils import *

router = Router()


@router.message(Command("config"))
@router.message(F.text.lower().split()[0] == 'config')
async def config_cmd(message: types.Message) -> None:
    help_text = (
        "🛠 <b>Настройка фильтров и правил пересылки:</b>\n\n"
        "<code>/keyremove {keyword}</code> — ключевые слова для удаления\n"
        "<code>/keyskip {keyword}</code> — ключевые слова для пропуска\n"
        "<code>/skip</code> — правила пересылки\n\n"
        "📌 Пример: <code>/keyskip ONON</code>"
    )

    await message.answer(help_text, parse_mode="HTML")

    parts = []

    keywords_to_remove = await get_removal_keywords()
    parts.append("🔴 <b>KeywordToRemove:</b>")
    parts.extend([f"  • <code>{keyword}</code>" for keyword in keywords_to_remove])

    keywords_to_skip = await get_skip_keywords()
    parts.append("\n🟡 <b>KeywordToSkip:</b>")
    parts.extend([f"  • <code>{keyword}</code>" for keyword in keywords_to_skip])

    rules = await ForwardRule.all()
    parts.append("\n🟢 <b>ForwardRule (✅ = skip ON):</b>")
    for rule in rules:
        src = f"{rule.chat_id}" + (f", {rule.thread_id}" if rule.thread_id else "")
        skip = "✅" if rule.skip else "❌"
        parts.append(f"  • [{rule.id}] {src} → {rule.target_chat_id} [{skip}]")

    await message.answer("\n".join(parts), disable_web_page_preview=True, parse_mode="HTML")


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
async def exit_cmd(message: types.Message) -> None:
    if message.chat.id == params.ADMIN_ID:
        await message.answer("Завершаю работу")

        import os
        os._exit(0)
