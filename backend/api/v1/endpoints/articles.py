from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.core.security import get_current_user
from backend.db.models import User
from backend.db.session import get_db
from backend.schemas.article import (ArticleResponse,
                                     ArticleCreate,
                                     ArticleUpdate)
from backend.crud.articles import (create,
                                   read,
                                   update,
                                   delete)

router = APIRouter(prefix='/articles')


@router.post('/create',
             status_code=status.HTTP_201_CREATED,
             openapi_extra={
                 'requestBody': {
                     'content': {
                         'application/json': {
                             'example': {
                                 'title': 'Заголовок статьи',
                                 'content': 'Содержимое статьи'
                             }
                         }
                     }
                 }
             },
             summary='Создать новую статью',
             description="""
             Эндпоинт, для создания новой статьи.
             Требуется авторизация
             """,
             tags=['Статьи'],
             responses={
                 status.HTTP_201_CREATED: {
                     'description': 'Статья успешно создана',
                     'content': {
                         'application/json': {
                             'example': {
                                 'message': 'Article created',
                                 'status': status.HTTP_201_CREATED
                             }

                         }
                     }
                 },
                 status.HTTP_401_UNAUTHORIZED: {
                     'description': 'Необходимо авторизоваться',
                     'content': {
                         'application/json': {
                             'example': {
                                 'status_code': status.HTTP_401_UNAUTHORIZED,
                                 'detail': 'Could not validate credentials',
                                 'headers': {'WWW-Authenticate': 'Bearer'},
                             }
                         }
                     }
                 },
                 status.HTTP_403_FORBIDDEN: {
                     'description': 'Необходимо подтвердить почту',
                     'content': {
                         'application/json': {
                             'example': {
                                 'status_code': status.HTTP_403_FORBIDDEN,
                                 'detail': 'You need to confirm email',
                             }
                         }
                     }
                 },
             }
             )
async def create_article(
        article: ArticleCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Создание новой статьи

    - **title**: Название статьи (обязательное поле)
    - **content**: Содержание статьи
    """
    return await create(current_user, article, db)


@router.get(
    '/', response_model=List[ArticleResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить список всех статей",
    description="""
    Возвращает список всех статей в системе.

    Особенности:
    - Возвращает пустой список, если статей нет
    - Статьи сортируются по дате создания (новые сначала)
    - Для каждой статьи возвращается краткая информация
    """,
    tags=['Статьи'],
    responses={
        status.HTTP_200_OK: {
            'description': 'Успешный запрос. Возвращает список статей',
            'content': {
                'application/json': {
                    'example': [
                        {
                            'id': 1,
                            'title': 'Первая статья',
                            'content': 'Краткое содержание...',
                            'author_name': 'Иван Иванов',
                            'created_at': '2023-01-01T12:00:00',
                            'updated_at': '2023-01-05T12:00:00',
                        },
                        {
                            'id': 2,
                            'title': 'Вторая статья',
                            'content': 'Еще одно краткое содержание...',
                            'author_name': 'Петр Петров',
                            'created_at': '2023-01-02T10:30:00',
                            'updated_at': '2023-01-07T12:00:00',

                        }
                    ]
                }
            }
        }
    }
)
async def show_article(db: Session = Depends(get_db)):
    """
        Получение списка статей

    Возвращает:
    - List[ArticleResponse]: Список объектов статей с основной информацией
    """
    return await read(db)


@router.get(
    '/{article_id:int}',
    response_model=ArticleResponse,
    status_code=status.HTTP_200_OK,
    summary='Получить конкретную статью',
    description="""
    Возвращает полную информацию о конкретной статье по её ID.

    Включает:
    - Полный текст статьи
    - Имя автора
    - Даты создания и обновления
    """,
    tags=['Статьи'],
    responses={
        status.HTTP_200_OK: {
            'description': 'Статья успешно найдена',
            'content': {
                'application/json': {
                    'example': {
                        'id': 1,
                        'title': 'Название статьи',
                        'content': 'Полный текст статьи...',
                        'author_name': 'Иван Иванов',
                        'created_at': '2023-01-01T12:00:00',
                        'updated_at': '2023-01-02T10:30:00'
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            'description': 'Статья не найдена',
            'content': {
                'application/json': {
                    'example': {
                        'status_code': status.HTTP_404_NOT_FOUND,
                        'detail': 'Article not found',

                    }
                }
            }
        }
    }
)
async def show_article(article_id: int, db: Session = Depends(get_db)):
    """
        Получение конкретной статьи

    Параметры:
    - article_id: ID запрашиваемой статьи (целое число)

    Возвращает:
    - ArticleResponse: Объект статьи со всей информацией
    """
    return await read(db, article_id)


@router.patch(
    '/update/{article_id:int}',
    status_code=status.HTTP_200_OK,
    summary='Обновить статью',
    description="""
    Обновляет данные статьи с возможностью частичного обновления полей.

    Требования:
    - Только автор статьи или администратор могут изменять статью
    - Доступно только для аутентифицированных пользователей
    """,
    tags=['Статьи'],
    responses={
        status.HTTP_200_OK: {
            'description': 'Статья успешно обновлена',
            'content': {
                'application/json': {
                    'example': {
                        'message': 'Article updated',
                        'status': status.HTTP_200_OK
                    }
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            'description': 'Не авторизован',
            'content': {
                'application/json': {
                    'example': {'detail': 'Not authenticated'}
                }
            }
        },
        status.HTTP_403_FORBIDDEN: {
            'description': 'Нет прав для редактирования статьи',
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
            'description': 'Статья не найдена',
            'content': {
                'application/json': {
                    'example': {
                        'status_code': status.HTTP_404_NOT_FOUND,
                        'detail': 'Article not found'
                    }
                }
            }
        }
    }
)
async def update_article(
        data: ArticleUpdate,
        article_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Обновление статьи

    Параметры:
    - article_id: ID статьи для обновления (целое число)
    - data: Данные для обновления (частичное обновление поддерживается)

    Возвращает:
    - dict: Сообщение об успешном обновлении и статус

    Ошибки:
    - 404: Если статья не найдена
    - 403: Если нет прав на удаление
    - 401: Если пользователь не авторизован
    """
    return await update(article_id, current_user, db, data)


@router.delete(
    '/delete/{article_id:int}',
    status_code=status.HTTP_200_OK,
    summary='Удалить статью',
    description="""
    Удаляет статью по её ID.
    
    Требования:
    - Только автор статьи или администратор могут удалять статью
    - Доступно только для аутентифицированных пользователей
    - Удаление невозможно восстановить
    """,
    tags=['Статьи'],
    responses={
        status.HTTP_200_OK: {
            'description': 'Статья успешно удалена',
            'content': {
                'application/json': {
                    'example': {
                        'message': 'Article deleted',
                        'status': status.HTTP_200_OK
                    }
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            'description': 'Не авторизован',
            'content': {
                'application/json': {
                    'example': {'detail': 'Not authenticated'}
                }
            }
        },
        status.HTTP_403_FORBIDDEN: {
            'description': 'Нет прав для удаления статьи',
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
            'description': 'Статья не найдена',
            'content': {
                'application/json': {
                    'example': {'detail': 'Article not found'}
                }
            }
        }
    }
)
async def delete_article(
        article_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Удаление статьи

    Параметры:
    - article_id: ID статьи для удаления (целое число)

    Возвращает:
    - dict: Сообщение об успешном удалении и статус

    Ошибки:
    - 404: Если статья не найдена
    - 403: Если нет прав на удаление
    - 401: Если пользователь не авторизован
    """
    return await delete(article_id, current_user, db)
