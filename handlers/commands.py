from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from core import get_keywords_to_remove, get_keywords_to_skip, get_channel_bypass_skip, get_thread_bypass_skip
from models import *


router = Router()


class ConfigStates(StatesGroup):
    waiting_for_keyword = State()
    waiting_for_channel_id = State()
    waiting_for_thread_id = State()


async def show_test_help(message: Message):
    help_text = (
        "🛠 Использование команды /config:\n\n"
        "<code>/config remove</code> - KEYWORDS_TO_REMOVE\n"
        "<code>/config skip</code> - KEYWORDS_TO_SKIP\n"
        "<code>/config channel</code> - CHANNEL_ID_BYPASS_SKIP\n"
        "<code>/config thread</code> - THREAD_ID_BYPASS_SKIP\n\n"
        "Пример: <code>/config remove ONON</code>"
    )

    await message.answer(help_text, parse_mode="HTML")

async def show_config(message: Message):
    config_text = "KEYWORDS_TO_REMOVE:\n"
    for item in await get_keywords_to_remove():
        config_text += f"- {item}\n"
    config_text += "\nKEYWORDS_TO_SKIP:\n"
    for item in await get_keywords_to_skip():
        config_text += f"- {item}\n"
    config_text += f"\nCHANNEL_ID_BYPASS_SKIP: {await get_channel_bypass_skip()}\n"
    config_text += f"\nTHREAD_ID_BYPASS_SKIP: {await get_thread_bypass_skip()}\n"

    await message.answer(config_text, parse_mode="HTML")


@router.message(Command("config"))
@router.message(F.text.lower().split()[0] == 'config')
async def config_category_callback(message: types.Message, state: FSMContext) -> None:
    parts = message.text.split()

    if len(parts) < 2:
        await show_test_help(message)
        return

    action = parts[1].lower()

    if action == 'remove':
        await message.answer("Введите ключевое слово для добавления/удаления в KEYWORDS_TO_REMOVE:")
        await state.set_state(ConfigStates.waiting_for_keyword)
        await state.update_data(category='remove')
    elif action == 'skip':
        await message.answer("Введите ключевое слово для добавления/удаления в KEYWORDS_TO_SKIP:")
        await state.set_state(ConfigStates.waiting_for_keyword)
        await state.update_data(category='skip')
    elif action == 'channel':
        await message.answer("Введите ID канала для добавления/удаления в CHANNEL_ID_BYPASS_SKIP:")
        await state.set_state(ConfigStates.waiting_for_channel_id)
    elif action == 'thread':
        await message.answer("Введите ID треда для добавления/удаления в THREAD_ID_BYPASS_SKIP:")
        await state.set_state(ConfigStates.waiting_for_thread_id)
    elif action == 'show':
        await show_config(message)
    else:
        await show_test_help(message)


@router.message(ConfigStates.waiting_for_keyword)
async def process_keyword(message: Message, state: FSMContext):
    try:
        keyword = message.text
        category = (await state.get_data())['category']
        if category == 'remove':
            exists = await KeywordToRemove.filter(keyword=keyword).first()
            if exists:
                await exists.delete()
                await message.answer(f"❌ Ключевое слово '{keyword}' удалено из KEYWORDS_TO_REMOVE")
            else:
                await KeywordToRemove.create(keyword=keyword)
                await message.answer(f"✅ Ключевое слово '{keyword}' добавлено в KEYWORDS_TO_REMOVE")
        elif category == 'skip':
            exists = await KeywordToSkip.filter(keyword=keyword).first()
            if exists:
                await exists.delete()
                await message.answer(f"❌ Ключевое слово '{keyword}' удалено из KEYWORDS_TO_SKIP")
            else:
                await KeywordToSkip.create(keyword=keyword)
                await message.answer(f"✅ Ключевое слово '{keyword}' добавлено в KEYWORDS_TO_SKIP")
    finally:
        await state.clear()


@router.message(ConfigStates.waiting_for_channel_id)
async def process_channel_id(message: Message, state: FSMContext):
    try:
        channel_id = int(message.text.strip())
        exists = await ChannelBypassSkip.filter(channel_id=channel_id).first()

        if exists:
            await exists.delete()
            await message.answer(f"❌ Канал с ID {channel_id} удален из CHANNEL_ID_BYPASS_SKIP")
        else:
            await ChannelBypassSkip.create(channel_id=channel_id)
            await message.answer(f"✅ Канал с ID {channel_id} добавлен в CHANNEL_ID_BYPASS_SKIP")
    except ValueError:
        await message.answer("⚠ ID канала должен быть числом")
    except Exception as e:
        await message.answer("⚠ Ошибка при обработке ID канала")
    finally:
        await state.clear()


@router.message(ConfigStates.waiting_for_thread_id)
async def process_thread_id(message: Message, state: FSMContext):
    try:
        thread_id = int(message.text.strip())
        exists = await ThreadBypassSkip.filter(thread_id=thread_id).first()

        if exists:
            await exists.delete()
            await message.answer(f"❌ Топик с ID {thread_id} удален из THREAD_ID_BYPASS_SKIP")
        else:
            await ThreadBypassSkip.create(thread_id=thread_id)
            await message.answer(f"✅ Топик с ID {thread_id} добавлен в THREAD_ID_BYPASS_SKIP")
    except ValueError:
        await message.answer("⚠ ID топика должен быть числом")
    except Exception as e:
        # logger.error(f"Error processing thread ID: {e}")
        await message.answer("⚠ Ошибка при обработке ID топика")
    finally:
        await state.clear()
