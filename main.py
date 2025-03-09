from fastapi import FastAPI
from api.v1.endpoints.articles import router as articles_router
import uvicorn

app = FastAPI()
app.include_router(articles_router)


@app.get('/')
async def root():
    return {'message':'Welcome to the Articles API!'}


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8080, reload=True)