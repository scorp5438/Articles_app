import asyncio
import os

import pytest
import requests

from backend.schemas.user import UserForEmail
from backend.fast_api_email.fast_api_email import send_email
from backend.tests.conftest import override_smtp_config, clear_mailhog
from backend.core.config import CONF

import socket


def check_localhost_connection(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0


def test_mailhog_connection():
    assert check_localhost_connection(8025), "MailHog is not reachable on localhost:8025"


def test_environment():
    assert os.getenv('VIRTUAL_ENV') is not None, "Not running in a virtual environment"
    print("Running in virtual environment:", os.getenv('VIRTUAL_ENV'))
    print("GITHUB_ACTIONS:", os.getenv('GITHUB_ACTIONS'))


import logging

logging.basicConfig(level=logging.INFO)


def test_mailhog_connection2():
    logging.info("Checking connection to MailHog on localhost:8025")
    assert check_localhost_connection(8025), "MailHog is not reachable on localhost:8025"


def test_mailhog_api_accessible():
    response = requests.get('http://localhost:8025/api/v2/messages')
    assert response.status_code == 200


# @pytest.mark.asyncio
# async def test_send_email_real_smtp(override_smtp_config, clear_mailhog):
#     test_user = UserForEmail(
#         email='test_user_13@mail.ru',
#         full_name='New Test User'
#     )
#
#     await send_email(
#         user=test_user,
#         subject='Test Email',
#         template_name='reg_confirm.html',
#         link='https://test.com'
#     )
#
#     url = 'http://localhost:8025/api/v2/messages'
#
#     for attempt in range(5):
#         try:
#             response = requests.get(url)
#             response.raise_for_status()
#             messages = response.json()
#             print(f"Attempt {attempt + 1}: Found {messages['count']} messages")  # Debug
#
#             if messages['count'] > 0:
#                 last_message = messages['items'][0]
#                 print("Last message:", last_message)  # Debug
#                 recipients = last_message['Content']['Headers']['To']
#                 subject = last_message['Content']['Headers']['Subject'][0]
#
#                 assert test_user.email in recipients
#                 assert 'Test Email' in subject
#                 return
#
#         except (requests.RequestException, KeyError) as e:
#             print(f"Attempt {attempt + 1} failed:", str(e))
#
#         await asyncio.sleep(2)
#
#     print("Full MailHog response:", response.text)
#     pytest.fail("Письмо не появилось в MailHog после 10 секунд ожидания")
#
#     # response = requests.get('http://localhost:8025/api/v2/messages')
#     # messages = response.json()
#     last_message = messages['items'][0]
#     recipients = last_message.get('Content').get('Headers').get('To')
#     subject = last_message['Content']['Headers']['Subject']
#
#     # assert response.status_code == 200
#     # assert len(messages['items']) > 0
#     assert test_user.email in recipients
#     assert 'Test Email' in subject


@pytest.mark.asyncio
async def test_send_email_real_smtp(override_smtp_config, clear_mailhog):
    # 1. Проверяем, что MailHog пуст
    response = requests.get('http://localhost:8025/api/v2/messages')
    assert response.json()['count'] == 0, "MailHog должен быть пуст перед тестом"

    # 2. Используем простой email, который точно примет MailHog
    test_user = UserForEmail(
        email='test@example.com',  # Важно использовать example.com
        full_name='Test User'
    )

    # 3. Добавляем диагностику
    print("Конфигурация SMTP:", {
        'server': CONF.MAIL_SERVER,
        'port': CONF.MAIL_PORT,
        'ssl': CONF.MAIL_SSL_TLS,
        'starttls': CONF.MAIL_STARTTLS
    })

    try:
        await send_email(
            user=test_user,
            subject='TEST SUBJECT',
            template_name='reg_confirm.html',
            link='https://example.com'
        )
    except Exception as e:
        pytest.fail(f"Ошибка отправки письма: {str(e)}")

    # 4. Увеличиваем время ожидания и добавляем проверки
    for attempt in range(10):  # 10 попыток с интервалом 1 секунда
        response = requests.get('http://localhost:8025/api/v2/messages')
        data = response.json()
        print(f"Попытка {attempt + 1}: найдено {data['count']} писем")

        if data['count'] > 0:
            message = data['items'][0]
            print("Полученное письмо:", message)
            assert test_user.email in message['Content']['Headers']['To']
            assert 'TEST SUBJECT' in message['Content']['Headers']['Subject'][0]
            return

        await asyncio.sleep(1)

    pytest.fail("Письмо не появилось в MailHog после 10 секунд ожидания")
