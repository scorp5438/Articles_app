from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.future import select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from argon2 import PasswordHasher

from db.models.user import User
from db.session import get_db
from schemas.user import TokenData

# Секретный ключ для подписи JWT
SECRET_KEY = 'VPVU3KCIYEKHb2BtaJlHYbpNeSAwEGYmViccL36NhceY1NQksHfv6KJ3/siNtKJr'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')

# Контекст для хэширования паролей
ph = PasswordHasher()

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
    return ph.verify(plain_password, hashed_password)


# Функция для хэширования пароля
def get_password_hash(password: str):
    return ph.hash(password)


async def get_current_user(
        token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
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
    return db