import asyncio

from tortoise import Tortoise

from core import *
from handlers import *


async def run_telethon_client():
    await connect_to_session()
    await client.start(config.PHONE)
    for handler in handlers:
        client.add_event_handler(handler)
    await client.run_until_disconnected()


async def run_aiogram_bot():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def init_db() -> None:
    print("Initializing database...")
    await Tortoise.init(
        db_url='sqlite://data/db/db.sqlite3',
        modules={'models': ['models']}
    )
    await Tortoise.generate_schemas()


async def on_startup() -> None:
    print("Bot starting up...")
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    dp.include_routers(*routers)

    await bot.delete_webhook(drop_pending_updates=False)  # False - to answer


async def on_shutdown() -> None:
    print("Bot shutting down...")
    await dp.storage.close()
    await dp.fsm.storage.close()

    # await bot.delete_webhook()
    await bot.session.close()


async def main() -> None:
    await init_db()

    await asyncio.gather(
        run_telethon_client(),
        run_aiogram_bot()
    )


if __name__ == '__main__':
    asyncio.run(main())
