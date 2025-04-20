import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    'tasks',
    broker=os.getenv('REDIS_URL'),
    backend=os.getenv('REDIS_URL'),
    include=['backend.tasks']
)


celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True
)














