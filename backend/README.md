# Articles App - RESTful API на FastAPI

Проект представляет собой RESTful API для управления пользователями, статьями и комментариями с аутентификацией через JWT и асинхронной отправкой email.

## 🚀 Функционал

- **Аутентификация**:
  - Регистрация с подтверждением по email
  - JWT-авторизация
- **Управление профилем**:
  - Просмотр/редактирование данных
- **Статьи и комментарии**:
  - CRUD для статей (только для подтвержденных пользователей)
  - Комментирование статей
- **Логирование** всех ключевых событий
- **Тестирование** (unit + интеграционные тесты)
- **CI/CD** через GitHub Actions

## 🛠 Технологии

- **Backend**: FastAPI (Python 3.10+)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
- **База данных**: PostgreSQL

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
- **Асинхронные задачи**: Celery + Redis

![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)
- **Деплой**: Docker + docker-compose

![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
- **Документация**: Swagger (автогенерация)

![Swagger](https://img.shields.io/badge/Swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)

## 📦 Установка

### Требования
- Docker 20.10+
- Docker Compose 2.0+

1. Клонируйте репозиторий:
```bash
   git clone https://github.com/scorp5438/Articles_app.git
   cd Articles_app
```
2. Создайте файл .env на основе .env.example и заполните настройки:
```bash
   cp .env.example .env
   nano .env  # или отредактируйте в любом редакторе
```

3. Запустите сервисы через docker-compose:
```bash
   sudo docker-compose up -d --build
```
4. При первом запуске выполните миграции:
```bash
   sudo docker ps
   sudo docker-compose exec {id контейнера fastapi} alembic upgrade head
```

5. Создайте суперпользователя (опционально):
```bash
   sudo docker-compose exec {id контейнера fastapi} python commands.py createsuperuser \
    --email admin@example.com \
    --password yourpassword \
    --fullname "Admin" \
    --noinput
```
   или
```bash
  sudo docker ps
  sudo docker-compose exec {id контейнера fastapi} /bin/bash
  cd commands
  python commands.py createsuperuser
```
И поочереди ввести email fullname и два раза password

## 🔧 Использование

* API доступно на http://localhost:8080
* Документация Swagger: http://localhost:8080/docs

## Примеры запросов:
    
### Регистрация

```bash
    curl -X POST "http://localhost:8080/api/v1/auth/register" \
      -H "Content-Type: application/json" \
      -d '{"email":"user@example.com","password":"string","full_name":"string"}'
```

### Создание статьи (требуется JWT)

```bash
    curl -X POST "http://localhost:8080/api/v1/articles/" \
      -H "Authorization: Bearer YOUR_JWT_TOKEN" \
      H "Content-Type: application/json" \
      -d '{"title":"string","content":"string"}'
```

## 🧪 Тестирование

```bash
    sudo docker ps
    sudo docker-compose exec {id контейнера fastapi} pytest
```
CI/CD автоматически запускает тесты при push в ветку main.

## 📂 Структура проекта

```commandline
backend/
├── alembic/       # Миграции БД
├── api/           # Эндпоинты API
├── commands/      # CLI-команды
├── core/          # Конфиги и security
├── crud/          # Операции с БД
├── db/            # Модели SQLAlchemy
├── fast_api_email # Отправка email
├── logs           # Логи приложения
├── schemas/       # Pydantic-схемы
├── tasks/         # Celery-таски
├── tests/         # Тесты
└── main.py        # Точка входа
.github/workflows/ # CI/CD конфигурация
```

## ⚠️ Важные замечания

1. Для работы email-рассылки необходимо настроить SMTP в .env
2. Redis используется как брокер для Celery
3. Все чувствительные данные (секреты) должны храниться в .env

## ⚙️ Конфигурация

```ini
# Безопасность
SECRET_KEY=секретный ключ

# БД
POSTGRES_DB=имя дб
POSTGRES_USER=имя пользователя
POSTGRES_PASSWORD=пароль
DB_HOST=db

# Email
MAIL_USERNAME=почта отправителя
MAIL_PASSWORD=пароль для использования почты в приложении
SUPPRESS_SEND=0

# Redis
REDIS_URL=redis://redis:6379/0
```

## 🔧 Важные параметры

1. Безопасность:
   * Обязательно измените SECRET_KEY в продакшене
2. Email:
   * Для тестов можно использовать MailHog (входит в docker-compose.yml)
    




















