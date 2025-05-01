import asyncio
import logging
import sys

from handlers import handlers
from core import *


async def on_startup() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # dp.include_routers(*routers)

    await bot.delete_webhook(drop_pending_updates=False)  # False - to answer


async def on_shutdown() -> None:
    await dp.storage.close()
    await dp.fsm.storage.close()

    # await bot.delete_webhook()
    await bot.session.close()


async def main() -> None:
    await init_db()

    await connect_to_session()
    await client.start(config.PHONE)
    for handler in handlers:
        client.add_event_handler(handler)
    await client.run_until_disconnected()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
