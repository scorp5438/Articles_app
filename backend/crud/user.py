from datetime import (datetime,
                      timedelta,
                      timezone)

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from pydantic import EmailStr
from backend.core.security import (get_password_hash,
                                   verify_timestamp_link,
                                   generate_timestamp_link)
from backend.core.config import (HOST,
                                 PORT)
from backend.db.models.user import User, Token
from backend.my_email.my_email import send_email
from backend.schemas.user import (UserCreate,
                                  UserResponse,
                                  UserUpdate)


async def get_user(db: Session, user_id: int = None, user_email: EmailStr | str = None):
    if user_id:
        result = await db.execute(select(User).filter(User.id == user_id))
    elif user_email:
        result = await db.execute(select(User).filter(User.email == user_email))
    else:
        result = await db.execute(select(User).order_by(User.id))
        return result.scalars().all()
    return result.scalars().first()


async def get_token(token: str, db: Session):
    result = await db.execute(select(Token).filter(Token.token == token))
    token = result.scalars().first()
    return token


async def add_token(token: str, db: Session):
    token_exist = await get_token(token, db)
    if token_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='token already exist'
        )

    token = Token(
        token=token,
        expire_at=(datetime.now(timezone.utc) + timedelta(minutes=30)).replace(tzinfo=None)
    )

    db.add(token)
    await db.commit()
    await db.refresh(token)


async def del_token(data: str, db: Session):
    *_, token = data.split()
    token = await get_token(token, db)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='token not found'
        )
    await db.delete(token)
    await db.commit()


async def create(user: UserCreate, db: Session):
    email = user.email
    db_user = await get_user(db, user_email=email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already registered'
        )

    hashed_password = get_password_hash(user.password)
    full_link = generate_timestamp_link()
    rand_part, *_ = full_link.split('_')

    confirmation_url = f"http://{HOST}:{PORT}/auth/reg-confirm/{full_link}"
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        conf_reg_link=rand_part,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    await send_email(
        new_user,
        'Подтверждение регистрации',
        'reg_confirm.html',
        confirmation_url
    )

    return {'message': 'Successfully registered', 'status': status.HTTP_201_CREATED}


async def activate(token: str, db: Session):
    rand_part, *_ = token.split('_')
    result = await db.execute(select(User).filter(User.conf_reg_link == rand_part))
    db_user = result.scalars().first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Confirm token invalid'
        )

    if not verify_timestamp_link(token):
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail='Token expired'
        )

    db_user.is_active = True
    db_user.conf_reg_link = None

    await db.commit()
    await db.refresh(db_user)

    return {'message': 'User activate'}


async def read(db: Session):
    users = await get_user(db)
    user_response = [
        UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            is_staff=user.is_staff,
            avatar_url=user.avatar_url,
        ) for user in users
    ]
    return user_response


async def update(data: UserUpdate, user_id: int, db: Session):
    user = await get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )

    update_data: dict = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {'message': 'update successfully', 'status': status.HTTP_200_OK}


async def delete(user_id: int, db: Session):
    user = await get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    await db.delete(user)
    await db.commit()
    return {'message': 'User deleted', 'status': status.HTTP_200_OK}
