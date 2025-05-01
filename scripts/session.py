from os import getenv

from dotenv import load_dotenv
from telethon.errors import SessionPasswordNeededError
from telethon.sync import TelegramClient

load_dotenv()

PHONE = getenv('PHONE')
API_ID = int(getenv('API_ID'))
API_HASH = getenv('API_HASH')
SESSION_NAME = getenv('SESSION_NAME')

client = TelegramClient(SESSION_NAME, API_ID, API_HASH, system_version='4.16.30-vxCUSTOM')

client.connect()

if not client.is_user_authorized():
    print('[*] Пользователь не авторизован. Начинаем процесс входа...')
    client.send_code_request(PHONE)
    code = input('Введите код, полученный в Telegram: ')

    try:
        client.sign_in(PHONE, code)
    except SessionPasswordNeededError:
        password = input('Введите пароль двухфакторной аутентификации: ')
        client.sign_in(password=password)

    print('[+] Авторизация прошла успешно. Сессия сохранена.')
else:
    print('[✓] Сессия уже авторизована. Повторная авторизация не требуется.')

me = client.get_me()
print(f"👤 Вы вошли как: {me.first_name} ({me.username})")

client.disconnect()
