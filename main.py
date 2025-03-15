from contextlib import asynccontextmanager

from fastapi import FastAPI
from api.v1.endpoints.articles import router as articles_router
from api.v1.endpoints.auth import router as auth_router
import uvicorn

from db.session import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(articles_router)
app.include_router(auth_router)


@app.get('/')
async def root():
    return {'message': 'Welcome to the Articles API!'}


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8080, reload=True)
