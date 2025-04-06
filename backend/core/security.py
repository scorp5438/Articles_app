from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets
import string

from sqlalchemy.orm import Session
from sqlalchemy.future import select
from fastapi import (Depends,
                     HTTPException,
                     status)
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from argon2 import PasswordHasher
from fastapi_mail import ConnectionConfig

from backend.core.config import BASE_DIR
from backend.db.models.user import (User,
                                    Token)
from backend.db.session import get_db
from backend.schemas.user import TokenData

# Секретный ключ для подписи JWT
SECRET_KEY = 'VPVU3KCIYEKHb2BtaJlHYbpNeSAwEGYmViccL36NhceY1NQksHfv6KJ3/siNtKJr'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')

# Контекст для хэширования паролей
ph = PasswordHasher()

# urls config
host = '0.0.0.0'
port = 8080

# Конфигурация my_email
conf = ConnectionConfig(
    MAIL_USERNAME='order_system@mail.ru',
    MAIL_PASSWORD='56R6ASz5pSeeDYuETz6v',
    MAIL_FROM='order_system@mail.ru',
    MAIL_PORT=465,
    MAIL_SERVER='smtp.mail.ru',
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    MAIL_FROM_NAME='Articles app',
    TEMPLATE_FOLDER=(BASE_DIR / 'my_email/templates'),
)


# Функция для создания JWT-токена
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Функция для проверки пароля
def verify_password(plain_password: str, hashed_password: str):
    return ph.verify(hashed_password, plain_password)


# Функция для хэширования пароля
def get_password_hash(password: str):
    return ph.hash(password)


async def get_current_user(
        token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    *_, token_exist = token.split()
    result = await db.execute(select(Token).filter(Token.token == token_exist))
    token_bd = result.scalars().first()

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    if not token_bd:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).filter(User.email == token_data.email))
    db_user = result.scalars().first()
    if db_user is None:
        raise credentials_exception
    return db_user


def generate_timestamp_link(length=24, expires_hours=1):
    timestamp = int(datetime.now().timestamp())
    rand_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
    return f'{rand_part}_{timestamp}_{expires_hours}'


def verify_timestamp_link(link: str):
    try:
        rand_part, timestamp_str, expires_hours_str = link.split('_')
        timestamp = int(timestamp_str)
        expires_hours = int(expires_hours_str)

        creation_time = datetime.fromtimestamp(timestamp)
        expires_time = creation_time + timedelta(hours=expires_hours)

        if datetime.now() > expires_time:
            return False
        return True
    except (ValueError, AttributeError):
        return False







