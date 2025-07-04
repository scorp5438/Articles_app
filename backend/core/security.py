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

from backend.db.models.user import (User,
                                    Token)
from backend.db.session import get_db
from backend.schemas.user import TokenData
from backend.core.config import  SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')

# Контекст для хэширования паролей
ph = PasswordHasher()

# Конфигурация fast_api_email



# Функция для создания JWT-токена
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
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







