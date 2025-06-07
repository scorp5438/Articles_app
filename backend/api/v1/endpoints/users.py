from typing import List
from fastapi import (APIRouter,
                     Depends,
                     status)

from sqlalchemy.orm import Session

from backend.core.security import get_current_user
from backend.db.session import get_db
from backend.db.models import User
from backend.schemas.user import (UserResponse,
                                  UserUpdate)
from backend.crud.user import (read,
                               update,
                               delete)

router = APIRouter(prefix='/users')


@router.get(
    '/users',
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary='Получить список пользователей',
    description="""
    Возвращает список всех пользователей системы.
    
    Требования:
    - Только для администраторов (is_staff=True)
    - Пользователь должен быть авторизован
    """,
    tags=['Пользователи'],
    responses={
        status.HTTP_200_OK: {
            'description': 'Список пользователей',
            'content': {
                'application/json': {
                    'example': [
                        {
                            'id': 1,
                            'email': 'admin@example.com',
                            'full_name': 'Администратор',
                            'is_active': True,
                            'created_at': '2023-01-01T00:00:00',
                            'is_staff': True,
                            'avatar_url': 'https://example.com/avatars/1.jpg'
                        },
                        {
                            'id': 2,
                            'email': 'user@example.com',
                            'full_name': 'Обычный пользователь',
                            'is_active': True,
                            'created_at': '2023-01-02T00:00:00',
                            'is_staff': False,
                            'avatar_url': None
                        }
                    ]
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
        status.HTTP_403_FORBIDDEN: {
            'description': 'Недостаточно прав',
            'content': {
                'application/json': {
                    'example': {
                        'status_code': status.HTTP_403_FORBIDDEN,
                        'detail': 'You don`t have permission'
                    }
                }
            }
        }
    }
)
async def get_users(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Получение списка пользователей

    Возвращает:
    - List[UserResponse]: Полный список пользователей системы

    Ошибки:
    - 403: Если пользователь не является администратором
    - 401: Если пользователь не авторизован
    """
    return await read(db, current_user, user_list=True)


@router.get(
    '/profile',
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary='Получить профиль текущего пользователя',
    description="""
    Возвращает профиль авторизованного пользователя.
    
    Требования:
    - Пользователь должен быть авторизован
    """,
    tags=['Пользователи'],
    responses={
        status.HTTP_200_OK: {
            'description': 'Профиль пользователя',
            'content': {
                'application/json': {
                    'example': {
                        'id': 1,
                        'email': 'user@example.com',
                        'full_name': 'Иван Иванов',
                        'is_active': True,
                        'created_at': '2023-01-01T00:00:00',
                        'is_staff': False,
                        'avatar_url': 'https://example.com/avatars/1.jpg'
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
        status.HTTP_404_NOT_FOUND: {
            'description': 'Пользователь не найден',
            'content': {
                'application/json': {
                    'example': {
                        'status_code': status.HTTP_404_NOT_FOUND,
                        'detail': 'User not found'
                    }
                }
            }
        }
    }
)
async def profile(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Получение профиля текущего пользователя

    Возвращает:
    - UserResponse: Полную информацию о текущем пользователе

    Ошибки:
    - 401: Если пользователь не авторизован
    - 404: Если пользователь не найден (крайне редкий случай)
    """
    return await read(db, current_user)


@router.patch(
    '/update/{user_id:int}',
    status_code=status.HTTP_200_OK,
    summary='Обновить данные пользователя',
    description="""
    Обновляет данные пользователя с возможностью частичного обновления.

    Требования:
    - Только администратор может обновлять данные других пользователей
    - Обычный пользователь может обновлять только свои данные
    - Только администратор может изменять поле is_staff
    """,
    tags=['Пользователи'],
    responses={
        status.HTTP_200_OK: {
            'description': 'Данные успешно обновлены',
            'content': {
                'application/json': {
                    'example': {
                        'message': 'Update successfully',
                        'status': status.HTTP_200_OK
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            'description': 'Некорректные данные',
            'content': {
                'application/json': {
                    'example': {'detail': 'Validation error'}
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
        status.HTTP_403_FORBIDDEN: {
            'description': 'Недостаточно прав',
            'content': {
                'application/json': {
                    'examples': {
                        'Not self or staff': {
                            'value': {
                                'status_code': status.HTTP_403_FORBIDDEN,
                                'detail': 'You don`t have permission'
                            }
                        },
                        'Staff field modification': {
                            'value': {
                                'status_code': status.HTTP_403_FORBIDDEN,
                                'detail': 'Only admin can change staff status'
                            }
                        }
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            'description': 'Пользователь не найден',
            'content': {
                'application/json': {
                    'example': {
                        'status_code': status.HTTP_404_NOT_FOUND,
                        'detail': 'User not found'

                    }
                }
            }
        }
    }
)
async def update_user(
        data: UserUpdate, user_id: int, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Обновление данных пользователя

    Параметры:
    - user_id: ID пользователя для обновления
    - data: Данные для обновления (частичное обновление поддерживается)

    Возвращает:
    - dict: Сообщение об успешном обновлении и статус

    Ошибки:
    - 400: Некорректные данные
    - 401: Не авторизован
    - 403: Недостаточно прав
    - 404: Пользователь не найден
    """
    return await update(user_id, current_user, db, data)


@router.delete(
    '/delete/{user_id:int}',
    status_code=status.HTTP_200_OK,
    summary='Удалить пользователя',
    description="""
    Удаляет пользователя из системы.
    
    Требования:
    - Только администратор может удалять других пользователей
    - Пользователь может удалить только свой аккаунт
    - Удаление невозможно отменить
    """,
    tags=['Пользователи'],
    responses={
        status.HTTP_200_OK: {
            'description': 'Пользователь успешно удален',
            'content': {
                'application/json': {
                    'example': {
                        'message': 'User deleted',
                        'status': status.HTTP_200_OK
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
        status.HTTP_403_FORBIDDEN: {
            'description': 'Недостаточно прав',
            'content': {
                'application/json': {
                    'example': {
                        'status_code': status.HTTP_403_FORBIDDEN,
                        'detail': 'You don`t have permission'
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            'description': 'Пользователь не найден',
            'content': {
                'application/json': {
                    'example': {
                        'status_code': status.HTTP_404_NOT_FOUND,
                        'detail': 'User not found'
                    }
                }
            }
        }
    }
)
async def delete_user(
        user_id: int, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Удаление пользователя

    Параметры:
    - user_id: ID пользователя для удаления

    Возвращает:
    - dict: Сообщение об успешном удалении и статус

    Ошибки:
    - 401: Не авторизован
    - 403: Недостаточно прав
    - 404: Пользователь не найден
    """
    return await delete(user_id, current_user, db)
