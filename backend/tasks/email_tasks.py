from backend.schemas.user import UserForEmail
from backend.fast_api_email.fast_api_email import send_email
from .celery_app import celery_app


@celery_app.task(name='send_email_task')
async def send_email_task(user: UserForEmail, subject: str, template_name: str, link: str):
    await send_email(user, subject, template_name, link)
