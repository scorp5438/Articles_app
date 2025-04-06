from pathlib import Path

from fastapi_mail import ConnectionConfig

BASE_DIR = Path(__file__).resolve().parent.parent

# RELOAD = True

# Секретный ключ для подписи JWT

# SECRET_KEY = 'VPVU3KCIYEKHb2BtaJlHYbpNeSAwEGYmViccL36NhceY1NQksHfv6KJ3/siNtKJr'
# ALGORITHM = 'HS256'
# ACCESS_TOKEN_EXPIRE_MINUTES = 60

# urls config

# HOST = '0.0.0.0'
# PORT = 8080

# Укажите URL вашей базы данных PostgreSQL
# Сама переменная SQLALCHEMY_DATABASE_URL не переезжает, будут только данные для подключения: user_art:1324@localhost/articles_db'
# SQLALCHEMY_DATABASE_URL = 'postgresql+asyncpg://user_art:1324@localhost/articles_db'

# Конфигурация my_email

# conf = ConnectionConfig(
#     MAIL_USERNAME='order_system@mail.ru',
#     MAIL_PASSWORD='56R6ASz5pSeeDYuETz6v',
#     MAIL_FROM='order_system@mail.ru',
#     MAIL_PORT=465,
#     MAIL_SERVER='smtp.mail.ru',
#     MAIL_STARTTLS=False,
#     MAIL_SSL_TLS=True,
#     MAIL_FROM_NAME='Articles app',
#     TEMPLATE_FOLDER='my_email/templates',
# )

# Настройки сложности пароля

# PATTERN_FULL = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%#?&])[A-Za-z\d@$!%#?&]{8,}$'
# PATTERN_LITE = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'
