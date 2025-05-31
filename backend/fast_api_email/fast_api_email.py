import datetime
import logging

from aiosmtplib import SMTPDataError

from fastapi_mail import FastMail, MessageSchema, MessageType

from backend.core.config import CONF
from backend.schemas.user import UserForEmail


logger_file = logging.getLogger('file_logger')

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
            template_name=template_name,
        )
    except SMTPDataError as smtp:
        logger_file.warning(f'Ошибка данных SMTP: {smtp}')

