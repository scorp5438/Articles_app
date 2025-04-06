# import datetime
#
# from fastapi_mail import FastMail, MessageSchema, MessageType
#
# from backend.core.security import conf
# from backend.db.models import User
#
#
# async def send_email(user: User, subject: str, template_name: str) -> None:
#     message = MessageSchema(
#         subject=subject,
#         recipients=[user.email],
#         template_body={
#             'full_name':user.full_name,
#             'current_year': datetime.datetime.now().year
#         },
#         subtype=MessageType.html
#     )
#
#     fm = FastMail(conf)
#     await fm.send_message(
#         message,
#         template_name=template_name
#     )
