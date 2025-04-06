from contextlib import asynccontextmanager

from fastapi import FastAPI
from api.v1.endpoints.articles import router as articles_router
from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.comments import router as comments_router
from api.v1.endpoints.users import router as users_router
import uvicorn

from backend.core.config import BASE_DIR
from backend.core.security import host, port
from db.session import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(articles_router)
app.include_router(auth_router)
app.include_router(comments_router)
app.include_router(users_router)


@app.get('/')
async def root():
    print(BASE_DIR)
    return {'message': 'Welcome to the Articles API!'}


if __name__ == '__main__':
    uvicorn.run('main:app', host=host, port=port, reload=True)
