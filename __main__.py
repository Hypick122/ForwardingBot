import asyncio

from tortoise import Tortoise

from config import *
from handlers import handlers, routers
from scripts.init_db_config import init_config
from utils import connect_to_session


async def run_telethon_client():
    logger.info(f"Starting Telethon client...")
    await connect_to_session()
    await client.start(params.PHONE)

    for handler, event in handlers:
        logger.debug(f"Registering handler: {handler.__name__} ({type(event).__name__})")
        client.add_event_handler(handler, event)

    await client.run_until_disconnected()


async def run_aiogram_bot():
    logger.info(f"Starting Aiogram polling...")
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def init_db() -> None:
    logger.info("Initializing database...")
    await Tortoise.init(
        db_url=params.DB_URL,
        modules={'models': ['models']}
    )
    await Tortoise.generate_schemas()


async def on_startup() -> None:
    logger.info("Aiogram bot is starting up...")

    dp.include_routers(*routers)

    await bot.delete_webhook(drop_pending_updates=False)  # False - to answer


async def on_shutdown() -> None:
    logger.info("Shutting down Aiogram bot...")
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
        import os

        os._exit(0)
