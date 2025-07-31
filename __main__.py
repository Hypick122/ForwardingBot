import asyncio

from tortoise import Tortoise

from config import *
from handlers import handlers, routers
from scripts.init_db_config import init_config
from utils import connect_to_session


async def run_telethon_client():
    await connect_to_session()
    await client.start(params.PHONE)
    for handler in handlers:
        client.add_event_handler(handler)
    await client.run_until_disconnected()


async def run_aiogram_bot():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def init_db() -> None:
    logger.info("Initializing database...")
    await Tortoise.init(
        db_url='sqlite://data/db/db.sqlite3',
        modules={'models': ['models']}
    )
    await Tortoise.generate_schemas()


async def on_startup() -> None:
    logger.info("Bot starting up...")

    dp.include_routers(*routers)

    await bot.delete_webhook(drop_pending_updates=False)  # False - to answer


async def on_shutdown() -> None:
    logger.info("Bot shutting down...")
    await dp.storage.close()
    await dp.fsm.storage.close()

    # await bot.delete_webhook()
    await bot.session.close()


async def main() -> None:
    await init_db()
    await init_config()

    await asyncio.gather(
        run_telethon_client(),
        run_aiogram_bot()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Bot stopped manually")
