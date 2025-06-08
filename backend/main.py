from fastapi import FastAPI, status
import uvicorn

from backend.api.v1.endpoints.auth import router as auth_router
from backend.api.v1.endpoints.users import router as users_router
from backend.api.v1.endpoints.articles import router as articles_router
from backend.api.v1.endpoints.comments import router as comments_router
from backend.core.config import HOST, PORT

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await create_tables()
#     yield


app = FastAPI(
    title='Articles API',
    version='0.0.0.0.1.0',
    description='Rest приложениe для создания, удаления и редактирования статей',
    contact={
        'name': 'Александр',
        'email': 'alex_77_90@mail.ru'
    }
)

app.include_router(articles_router)
app.include_router(auth_router)
app.include_router(comments_router)
app.include_router(users_router)


@app.get(
    '/',
    status_code=status.HTTP_200_OK,
    summary='Корневой эндпоинт API',
    description="""
    Возвращает приветственное сообщение API.
    Используется для проверки работоспособности сервиса.
    """,
    tags=['Сервис'],
    responses={
        status.HTTP_200_OK: {
            'description': 'API работает корректно',
            'content': {
                'application/json': {
                    'example': {
                        'message': 'Welcome to the Articles API!'
                    }
                }
            }
        }
    }
)
async def root():
    """
        Корневой эндпоинт

    Возвращает:
    - dict: Приветственное сообщение

    Использование:
    - Проверка доступности API
    - Тестирование подключения
    """
    return {'message': 'Welcome to the Articles API!'}


if __name__ == '__main__':
    uvicorn.run('main:app', host=HOST, port=PORT, reload=True)
