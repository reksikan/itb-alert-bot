from os import environ

TELEGRAM_TOKEN = environ.get('TELEGRAM_TOKEN', '5069566480:AAHLCoxGkzWdbspLj-HU38kcvpYkfpi-Bl0')
TELEGRAM_ALERT_CHAT_ID = environ.get('TELEGRAM_ALERT_CHAT_ID')

# Database settings
POSTGRES_HOST = environ.get('POSTGRES_HOST', '127.0.0.1')
POSTGRES_PORT = environ.get('POSTGRES_PORT', '5432')
POSTGRES_LOGIN = environ.get('POSTGRES_LOGIN', 'postgres')
POSTGRES_PASSWORD = environ.get('POSTGRES_PASSWORD', 'postgres')

POSTGRES_DATABASE = environ.get('POSTGRES_DATABASE', 'itb_alerts')
POSTGRES_URL = (
    f'postgresql+asyncpg://{POSTGRES_LOGIN}:{POSTGRES_PASSWORD}@'
    f'{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}'
)

POSTGRES_TEST_DATABASE = environ.get('POSTGRES_TEST_DATABASE', 'test_' + POSTGRES_DATABASE)
POSTGRES_TEST_URL = (
    f'postgresql+asyncpg://{POSTGRES_LOGIN}:{POSTGRES_PASSWORD}@'
    f'{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_TEST_DATABASE}'
)
