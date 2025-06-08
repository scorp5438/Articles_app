# Articles App - RESTful API на FastAPI

Проект представляет собой RESTful API для управления пользователями, статьями и комментариями с аутентификацией через JWT и асинхронной отправкой email.

## 🚀 Функционал

- **Аутентификация**:
  - Регистрация с подтверждением по email
  - JWT-авторизация
  - Восстановление пароля
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
- **База данных**: PostgreSQL
- **Асинхронные задачи**: Celery + Redis
- **Деплой**: Docker + docker-compose
- **Документация**: Swagger (автогенерация)

## 📦 Установка

1. Клонируйте репозиторий:
```bash
   git clone https://github.com/scorp5438/Articles_app.git
   cd Articles_app
```

2. Запустите сервисы через docker-compose:
```bash
   docker-compose up -d --build
```
3. При первом запуске выполните миграции:
```bash
   docker-compose exec {id контейнера fastapi} alembic upgrade head
```

4. Создайте суперпользователя (опционально):
```bash
   docker-compose exec {id контейнера fastapi} python commands.py createsuperuser \
    --email admin@example.com \
    --password yourpassword \
    --fullname "Admin" \
    --noinput
```
   или
```bash
  docker-compose exec {id контейнера fastapi} /bin/bash
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
    docker-compose exec {id контейнера fastapi} pytest
```
CI/CD автоматически запускает тесты при push в ветку main.

## 📂 Структура проекта

```commandline
backend/
├── alembic/       # Миграции БД
├── api/           # Эндпоинты API
├── commands/      # Команда для создвния суперпользователя
├── core/          # Конфиги и security
├── crud/          # Операции с БД
├── db/            # Модели SQLAlchemy
├── fast_api_email # Модуль отправка писем
├── logs           # Файлы логов
├── schemas/       # Pydantic-схемы
├── tasks/         # Celery-таски
├── tests/         # Тесты
.github/workflows/ # CI/CD конфигурация
```

## ⚠️ Важные замечания

1. Для работы email-рассылки необходимо настроить SMTP в .env
2. Redis используется как брокер для Celery
3. Все чувствительные данные (секреты) должны храниться в .env

## ⚙️ Конфигурация

```ini
SECRET_KEY=секретный ключ

POSTGRES_DB=имя дб
POSTGRES_USER=имя пользователя
POSTGRES_PASSWORD=пароль
DB_HOST=db


MAIL_USERNAME=почта отправителя
MAIL_PASSWORD=пароль для использования почты в приложении
SUPPRESS_SEND=0

REDIS_URL=redis://redis:6379/0
```

## 🔧 Важные параметры

1. Безопасность:
   * Обязательно измените SECRET_KEY в продакшене
2. Email:
   * Для тестов можно использовать MailHog (входит в docker-compose.yml)
    




















