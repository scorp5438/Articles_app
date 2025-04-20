import os
from pathlib import Path
from dotenv import load_dotenv

from fastapi_mail import ConnectionConfig

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Секретный ключ для подписи JWT

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# urls config

HOST = '0.0.0.0'
PORT = 8080

# Укажите URL вашей базы данных PostgreSQL

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

SQLALCHEMY_DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'

# Конфигурация email

CONF = ConnectionConfig(
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_FROM=os.getenv('MAIL_USERNAME'),
    MAIL_PORT=465,
    MAIL_SERVER='smtp.mail.ru',
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    MAIL_FROM_NAME='Articles app',
    TEMPLATE_FOLDER=(BASE_DIR / 'fast_api_email/templates'),
)

# Настройки сложности пароля

PATTERN_FULL = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%#?&])[A-Za-z\d@$!%#?&]{8,}$'
PATTERN_LITE = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'
