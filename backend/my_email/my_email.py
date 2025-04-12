import datetime

from fastapi_mail import FastMail, MessageSchema, MessageType

from backend.core.config import CONF
from backend.db.models import User


async def send_email(
        user: User,
        subject: str,
        template_name: str,
        link: str
) -> None:

    message = MessageSchema(
        subject=subject,
        recipients=[user.email],
        template_body={
            'full_name':user.full_name,
            'current_year': datetime.datetime.now().year,
            'link': link
        },
        subtype=MessageType.html
    )

    fm = FastMail(CONF)
    await fm.send_message(
        message,
        template_name=template_name
    )
