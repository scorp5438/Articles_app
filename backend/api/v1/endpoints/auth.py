from datetime import timedelta
from fastapi import (APIRouter,
                     Depends,
                     HTTPException,
                     status)

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from argon2.exceptions import VerifyMismatchError

from backend.core.security import (verify_password,
                                   create_access_token,
                                   oauth2_scheme,
                                   get_current_user)
from backend.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from backend.db.session import get_db
from backend.schemas.user import (Token,
                                  UserCreate)

from backend.crud.user import (create,
                               get_user,
                               add_token,
                               del_token,
                               activate)
from backend.db.models import User
from backend.crud.user import send_link

router = APIRouter(prefix='/auth')


@router.post(
    '/login',
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary='Аутентификация пользователя',
    description="""
    Аутентификация пользователя по email и паролю.
    
    Возвращает JWT токен для доступа к защищенным эндпоинтам.
    Токен необходимо передавать в заголовке Authorization: Bearer <token>
    """,
    tags=['Аутентификация'],
    responses={
        status.HTTP_200_OK: {
            'description': 'Успешная аутентификация',
            'content': {
                'application/json': {
                    'example': {
                        'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                        'token_type': 'bearer'
                    }
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            'description': 'Ошибка аутентификации',
            'content': {
                'application/json': {
                    'examples': {
                        'User not found': {
                            'value': {
                                'status_code': status.HTTP_401_UNAUTHORIZED,
                                'detail': 'User not found'
                            }
                        },
                        'Incorrect password': {
                            'value': {
                                'status_code': status.HTTP_401_UNAUTHORIZED,
                                'detail': 'Incorrect login or password',
                            }
                        }
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            'description': 'Некорректный запрос',
            'content': {
                'application/json': {
                    'example': {'detail': 'Invalid request format'}
                }
            }
        }
    }
)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
        Вход в систему

    Параметры:
    - username: Email пользователя (передается как username)
    - password: Пароль пользователя

    Возвращает:
    - Token: JWT токен доступа

    Ошибки:
    - 401: Неверный email или пароль
    - 400: Некорректный формат запроса
    """
    email = form_data.username
    db_user = await get_user(db, user_email=email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found'
        )
    try:
        verify_password(form_data.password, db_user.hashed_password)
    except VerifyMismatchError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect login or password',
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': db_user.email}, expires_delta=access_token_expires
    )
    await add_token(access_token, db)
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post(
    '/logout',
    status_code=status.HTTP_200_OK,
    summary='Выход из системы',
    description="""
    Завершает текущую сессию пользователя.
    
    Требования:
    - Действующий JWT токен в заголовке Authorization
    - Токен будет добавлен в черный список и станет недействительным
    """,
    tags=['Аутентификация'],
    responses={
        status.HTTP_200_OK: {
            'description': 'Успешный выход из системы',
            'content': {
                'application/json': {
                    'example': {
                        'message': 'Successfully logged out',
                        'status': 200
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            'description': 'Не авторизован (неверный/отсутствующий токен)',
            'content': {
                'application/json': {
                    'example': {
                        'status_code': status.HTTP_400_BAD_REQUEST,
                        'detail': 'token not found'
                    }
                }
            }
        }
    }
)
async def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
        Выход из системы

    Параметры:
    - Требуется JWT токен в заголовке Authorization

    Возвращает:
    - dict: Сообщение об успешном выходе и статус

    Ошибки:
    - 401: Если токен отсутствует или недействителен
    """
    await del_token(token, db)
    return {'message': 'Successfully logged out', 'status': status.HTTP_200_OK}


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    summary='Регистрация нового пользователя',
    description="""
    Создает нового пользователя в системе.

    Особенности:
    - Пароль хешируется перед сохранением
    - После регистрации отправляется ссылка для подтверждения email
    - Email должен быть уникальным
    """,
    tags=['Аутентификация'],
    responses={
        status.HTTP_201_CREATED: {
            'description': 'Пользователь успешно зарегистрирован',
            'content': {
                'application/json': {
                    'example': {
                        'message': 'Successfully registered',
                        'status': status.HTTP_201_CREATED
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            'description': 'Ошибка регистрации',
            'content': {
                'application/json': {
                    'examples': {
                        'Email exists': {
                            'value': {
                                'status_code': status.HTTP_400_BAD_REQUEST,
                                'detail': 'Email already registered'
                            }
                        },
                        'Invalid data': {
                            'value': {'detail': 'Validation error'}
                        }
                    }
                }
            }
        }
    }
)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
        Регистрация нового пользователя

    Параметры:
    - email: Email пользователя (должен быть уникальным)
    - password: Пароль пользователя
    - full_name: Полное имя пользователя

    Возвращает:
    - dict: Сообщение об успешной регистрации и статус

    Ошибки:
    - 400: Если email уже зарегистрирован или неверные данные
    """
    return await create(user, db)


@router.get(
    '/reg-confirm/{full_link}',
    status_code=status.HTTP_200_OK,
    summary='Подтверждение регистрации',
    description="""
    Подтверждает регистрацию пользователя по уникальной ссылке.
    
    Особенности:
    - Ссылка содержит временной штамп и должна быть использована в течение определенного времени
    - После подтверждения аккаунт становится активным
    - Ссылка может быть использована только один раз
    """,
    tags=['Аутентификация'],
    responses={
        status.HTTP_200_OK: {
            'description': 'Аккаунт успешно подтвержден',
            'content': {
                'application/json': {
                    'example': {
                        'message': 'User activate'
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            'description': 'Неверная ссылка подтверждения',
            'content': {
                'application/json': {
                    'example': {
                        'status_code': status.HTTP_404_NOT_FOUND,
                        'detail': 'Confirm token invalid'
                    }
                }
            }
        },
        status.HTTP_408_REQUEST_TIMEOUT: {
            'description': 'Ссылка подтверждения устарела',
            'content': {
                'application/json': {
                    'example': {
                        'status_code': status.HTTP_408_REQUEST_TIMEOUT,
                        'detail': 'Token expired'
                    }
                }
            }
        }
    }
)
async def reg_confirm(
        full_link: str,
        db: Session = Depends(get_db)
):
    """
        Подтверждение регистрации пользователя

    Параметры:
    - full_link: Уникальная ссылка подтверждения (содержит временной штамп)

    Возвращает:
    - dict: Сообщение об успешном подтверждении

    Ошибки:
    - 404: Если ссылка недействительна
    - 408: Если ссылка устарела
    """
    return await activate(full_link, db)


@router.get(
    '/get_link',
    status_code=status.HTTP_200_OK,
    summary='Получить ссылку подтверждения',
    description="""
    Отправляет ссылку для подтверждения email на почту пользователя.
    
    Требования:
    - Пользователь должен быть авторизован
    - Аккаунт не должен быть уже подтвержден
    """,
    tags=['Аутентификация'],
    responses={
        status.HTTP_200_OK: {
            'description': 'Ссылка успешно отправлена',
            'content': {
                'application/json': {
                    'example': {
                        'message': 'link was sent'
                    }
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            'description': 'Пользователь не авторизован',
            'content': {
                'application/json': {
                    'example': {'detail': 'Not authenticated'}
                }
            }
        },
    }
)
async def get_link(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Запрос ссылки для подтверждения email

    Возвращает:
    - dict: Сообщение об отправке ссылки

    Ошибки:
    - 401: Если пользователь не авторизован
    """
    await send_link(current_user, db)
    return {'message': 'link was sent'}
