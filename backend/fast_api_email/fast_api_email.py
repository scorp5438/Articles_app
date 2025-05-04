import datetime
from aiosmtplib import SMTPDataError

from fastapi import (status,
                     HTTPException)
from fastapi_mail import FastMail, MessageSchema, MessageType

from backend.core.config import CONF
from backend.schemas.user import UserForEmail


async def send_email(
        user: UserForEmail,
        subject: str,
        template_name: str,
        link: str
) -> None:
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[user.email],
            template_body={
                'full_name': user.full_name,
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
    except SMTPDataError as smtp:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ошибка данных SMTP: {smtp}'
        )

