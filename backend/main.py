from fastapi import FastAPI
import uvicorn
import sys
from pathlib import Path


sys.path.append(str(Path(__file__).parent.parent))
from backend.commands.commands import execute_from_command_line
from backend.api.v1.endpoints.auth import router as auth_router
from backend.api.v1.endpoints.users import router as users_router
from backend.api.v1.endpoints.articles import router as articles_router
from backend.api.v1.endpoints.comments import router as comments_router
from backend.core.config import HOST, PORT

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await create_tables()
#     yield


app = FastAPI()
app.include_router(articles_router)
app.include_router(auth_router)
app.include_router(comments_router)
app.include_router(users_router)


@app.get('/')
async def root():
    return {'message': 'Welcome to the Articles API!'}


if __name__ == '__main__':
    execute_from_command_line()
    uvicorn.run('main:app', host=HOST, port=PORT, reload=True)
