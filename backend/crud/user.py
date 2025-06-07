import logging
from datetime import (datetime,
                      timedelta,
                      timezone)

from fastapi import (HTTPException,
                     status)
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from pydantic import EmailStr

from backend.core.security import (get_password_hash,
                                   verify_timestamp_link,
                                   generate_timestamp_link)
from backend.core.config import (HOST,
                                 PORT)
from backend.db.models.user import (User,
                                    Token)

from backend.schemas.user import (UserCreate,
                                  UserResponse,
                                  UserUpdate,
                                  UserForEmail)
from backend.tasks.email_tasks import send_email_task
from backend.core.decorators import check_is_staff_or_self_permissions

logger_console = logging.getLogger('console_logger')
logger_file = logging.getLogger('file_logger')


async def get_user(db: Session, user_id: int = None, user_email: EmailStr | str = None):
    if user_id:
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if user is None:
            logger_file.warning('User not found')
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='user not found'
            )
    elif user_email:
        result = await db.execute(select(User).filter(User.email == user_email))
        user = result.scalars().first()
    else:
        result = await db.execute(select(User).order_by(User.id))
        return result.scalars().all()

    return user


async def get_token(token: str, db: Session):
    result = await db.execute(select(Token).filter(Token.token == token))
    token = result.scalars().first()
    return token


async def add_token(token: str, db: Session):
    token_exist = await get_token(token, db)
    if token_exist:
        logger_file.warning('token already exist')
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
    logger_console.info('token add successfully')


async def del_token(data: str, db: Session):
    *_, token = data.split()
    token = await get_token(token, db)
    if not token:
        logger_file.warning('token not found')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='token not found'
        )
    await db.delete(token)
    await db.commit()
    logger_console.info('token deleted')

async def send_link(user: User, db: Session):
    full_link = generate_timestamp_link()
    rand_part, *_ = full_link.split('_')
    confirmation_url = f"http://{HOST}:{PORT}/auth/reg-confirm/{full_link}"
    db_user = await get_user(db, user_email=user.email)
    db_user.conf_reg_link = rand_part

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    user_data = UserForEmail.model_validate(db_user)

    await send_email_task(
        user=user_data,
        subject='Подтверждение регистрации',
        template_name='reg_confirm.html',
        link=confirmation_url
    )

async def create(user: UserCreate, db: Session):
    email = user.email
    db_user = await get_user(db, user_email=email)
    if db_user:
        logger_file.warning('Email already registered')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already registered'
        )

    hashed_password = get_password_hash(user.password)
    # full_link = generate_timestamp_link()
    # rand_part, *_ = full_link.split('_')
    #
    # confirmation_url = f"http://{HOST}:{PORT}/auth/reg-confirm/{full_link}"
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        # conf_reg_link=rand_part,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    logger_console.info('Successfully registered')

    await send_link(new_user, db)
    # user_data = UserForEmail.model_validate(new_user)
    # await send_email_task(
    #     user=user_data,
    #     subject='Подтверждение регистрации',
    #     template_name='reg_confirm.html',
    #     link=confirmation_url
    # )
    return {'message': 'Successfully registered', 'status': status.HTTP_201_CREATED}


async def activate(token: str, db: Session):
    rand_part, *_ = token.split('_')
    result = await db.execute(select(User).filter(User.conf_reg_link == rand_part))
    db_user = result.scalars().first()

    if not db_user:
        logger_file.warning('Confirm token invalid')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Confirm token invalid'
        )

    if not verify_timestamp_link(token):
        logger_file.warning('Token expired')
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail='Token expired'
        )

    db_user.is_active = True
    db_user.conf_reg_link = None

    await db.commit()
    await db.refresh(db_user)
    logger_console.info('User activate')

    return {'message': 'User activate'}


async def read(db: Session, current_user: User, user_list=False):
    if current_user.is_staff and user_list:
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
    elif not user_list:
        user = await get_user(db, user_id=current_user.id)
        user_response = UserResponse.model_validate(user)
    else:
        logger_file.warning('You don`t have permission')
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You don`t have permission'
        )
    return user_response


@check_is_staff_or_self_permissions
async def update(user_id: int, current_user, db: Session, data: UserUpdate):
    user = await get_user(db, user_id=user_id)
    if not user:
        logger_file.warning('User not found')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )

    update_data: dict = data.model_dump(exclude_unset=True)

    if 'is_staff' in update_data.keys() and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You don`t have permission'
        )

    for key, value in update_data.items():
        setattr(user, key, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger_console.info('Update successfully')
    return {'message': 'Update successfully', 'status': status.HTTP_200_OK}


@check_is_staff_or_self_permissions
async def delete(user_id: int, current_user, db: Session):
    user = await get_user(db, user_id=user_id)
    if not user:
        logger_file.warning('User not found')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    await db.delete(user)
    await db.commit()
    logger_console.info('User deleted')
    return {'message': 'User deleted', 'status': status.HTTP_200_OK}
