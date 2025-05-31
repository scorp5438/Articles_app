import os
from logging.config import dictConfig
from pathlib import Path
from dotenv import load_dotenv

from fastapi_mail import ConnectionConfig

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Секретный ключ для подписи JWT

SECRET_KEY = os.getenv('SECRET_KEY', 'test_secret_key')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# urls config

HOST = '0.0.0.0'
PORT = 8080

# Укажите URL вашей базы данных PostgreSQL

POSTGRES_USER = os.getenv('POSTGRES_USER', 'test_user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'test_password')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'test_db')
DB_HOST = os.getenv('DB_HOST', 'localhost')

SQLALCHEMY_DATABASE_URL = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}/{POSTGRES_DB}'

# Конфигурация email

CONF = ConnectionConfig(
    MAIL_USERNAME=os.getenv('MAIL_USERNAME', 'test@example.com'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD', 'test_password'),
    MAIL_FROM=os.getenv('MAIL_USERNAME', 'test@example.com'),
    MAIL_PORT=465,
    MAIL_SERVER='smtp.mail.ru',
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    MAIL_FROM_NAME='Articles app',
    TEMPLATE_FOLDER=(BASE_DIR / 'fast_api_email/templates'),
    SUPPRESS_SEND=os.getenv('SUPPRESS_SEND', '1') == '1'
)

# Настройки сложности пароля

PATTERN_FULL = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%#?&])[A-Za-z\d@$!%#?&]{8,}$'
PATTERN_LITE = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'

logs_dir = os.path.join(BASE_DIR, 'logs')
os.makedirs(logs_dir, exist_ok=True)

logging_config = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': os.getenv('LOG_LEVEL_STREAM', 'DEBUG'),
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'level': os.getenv('LOG_LEVEL_FILE', 'INFO'),
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': str(BASE_DIR / 'logs' / 'articles_app.log'),
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 5,
            'encoding': 'utf8'
        },
    },
    'loggers': {
        'console_logger': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'file_logger': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO'
    }
}

dictConfig(logging_config)
