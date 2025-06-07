FROM python:3.12

# 1. Устанавливаем Poetry (официальный способ)
ENV POETRY_VERSION=2.1.2
ENV POETRY_HOME=/opt/poetry
ENV PATH="${POETRY_HOME}/bin:${PATH}"

# Устанавливаем зависимости, необходимые для curl и установки Poetry
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Скачиваем и устанавливаем Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# 2. Отключаем создание виртуального окружения (ставим в системный Python)
RUN poetry config virtualenvs.create false


# 3. Копируем зависимости и устанавливаем их
WORKDIR /app/backend
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi --only main --no-root

# 4. Копируем остальной код
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]