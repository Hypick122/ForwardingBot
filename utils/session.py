from telethon.errors import SessionPasswordNeededError

from config import *

__all__ = (
    'connect_to_session',
)


async def connect_to_session() -> None:
    await client.connect()

    if not await client.is_user_authorized():
        logger.info("[*] Не авторизован. Запрос кода...")
        await client.send_code_request(config.PHONE)
        code = input('Код из Telegram: ')
        try:
            await client.sign_in(config.PHONE, code)
        except SessionPasswordNeededError:
            password = input('Пароль 2FA: ')
            await client.sign_in(password=password)
        logger.info("[+] Авторизация прошла успешно.")
    else:
        logger.info("[✓] Уже авторизован.")

    user = await client.get_me()
    logger.info(f"👤 Вы вошли как: {user.first_name} (@{user.username})")
