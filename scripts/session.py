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
    print('[*] Не авторизован. Запрос кода...')
    client.send_code_request(PHONE)
    code = input('Код из Telegram: ')

    try:
        client.sign_in(PHONE, code)
    except SessionPasswordNeededError:
        password = input('Пароль 2FA: ')
        client.sign_in(password=password)

    print('[+] Авторизация прошла успешно.')
else:
    print('[✓] Уже авторизован.')

me = client.get_me()
print(f"👤 Вы вошли как: {me.first_name} ({me.username})")

client.disconnect()
