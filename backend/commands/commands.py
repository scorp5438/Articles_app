import argparse
import asyncio
import re
from getpass import getpass
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.core.security import get_password_hash
from backend.core.config import PATTERN_LITE, PATTERN_EMAIL
from backend.crud.user import get_user
from backend.db.session import get_db, AsyncSessionLocal
from backend.db.models import User


def parse_args():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description='Управление данными в приложении'
    )
    subparser = parser.add_subparsers(dest='command', help='Доступные команды')
    create_superuser = subparser.add_parser(
        'createsuperuser',
        help='Создание суперпользователя'
    )

    create_superuser.add_argument('--email', help='email (login)')
    create_superuser.add_argument('--password', help='Password')
    create_superuser.add_argument('--fullname', help='Full name')
    create_superuser.add_argument('--noinput', action='store_true', help='request')

    return parser.parse_args()


def is_password_weak(password: str) -> bool:
    return re.match(PATTERN_LITE, password) is None


def is_walid_email(email: str) -> bool:
    return re.match(PATTERN_EMAIL, email) is None


async def is_exist_email(email: str) -> bool:
    async with AsyncSessionLocal() as db:
        db_user = await get_user(db, user_email=email)
    return db_user is None


async def interactive_create_superuser() -> tuple[str, str, str]:
    """Интерактивное создание суперпользователя"""
    print('===Create superuser===')
    email = input('Email: ').strip()
    while not email or is_walid_email(email):
        print(f'Ошибка: некорректная почта {email} или не заполнена')
        email = input('Email: ').strip()

    while await is_exist_email(email):
        print(f'Ошибка: пользователь с почтой {email} существует')
        email = input('Email: ').strip()

    fullname = input('Fullname: ').strip()
    while not fullname:
        print('Ошибка: имя пользователя не может быть пустым')
        fullname = input('Username: ').strip()

    while True:
        password = getpass('Password: ').strip()
        if not password:
            print('Ошибка: пароль не может быть пустым')
            password = getpass('Password: ').strip()
            continue

        password_confirm = getpass('Password: ').strip()
        if password != password_confirm:
            print("Ошибка: пароли не совпадают")
            continue

        if is_password_weak(password):
            print("\nПредупреждение: ваш пароль слишком простой!")
            print("Рекомендуется:")
            print("- Минимум 8 символов")
            print("- Буквы и цифры")

            confirm = input("\nВы уверены, что хотите использовать этот пароль? (y/n): ").lower()
            if confirm != 'y':
                continue

        break

    print(f'{email = } {password = } {fullname = }')
    return email, password, fullname


async def create_superuser_in_db(email: str, password: str, fullname: str) -> bool:
    """Создание суперпользователя в базе данных"""
    if await is_exist_email(email):
        print(f'Ошибка: пользователь с почтой {email} уже существует')
        return False

    new_user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=fullname,
        is_active=True,
        is_staff=True,
    )
    async with AsyncSessionLocal() as db:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    return True


async def execute_from_command_line():
    """Точка входа для выполнения команд"""
    args = parse_args()
    if args.command == 'createsuperuser':
        if args.noinput or args.email or args.password or args.fullname:
            if not args.email or not args.password or not args.fullname:
                print('Ошибка: в noinput режиме необходимо указывать --email, --password и --fullname')
                return

            email = args.email
            password = args.password
            fullname = args.fullname

            if is_password_weak(password) and not args.noinput:
                print('Предупреждение: пароль слишком простой!')

            if is_walid_email(email) and not args.noinput:
                print(f'Предупреждение: некорректная почта: {email}')

        else:
            # Интерактивный режим
            email, password, fullname = await interactive_create_superuser()

        success = await create_superuser_in_db(email, password, fullname, db)
        if success:
            print(f"\nСуперпользователь '{fullname}' успешно создан!")
            print(f"Email: {email}")
            print(f"Password: {'*' * len(password)}")

    else:
        print(f"Неизвестная команда: {args.command}")
        print("Доступные команды: createsuperuser")


async def main():
    await execute_from_command_line()


if __name__ == '__main__':
    asyncio.run(main())
