FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем зависимости ПЕРЕД копированием кода
COPY engines/indicator-engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ВЕСЬ бэкенд
COPY . .

# PYTHONPATH гарантирует, что импорты 'common' и 'api_v2' будут работать
ENV PYTHONPATH=/app

CMD ["python3", "engines/indicator-engine/scheduler.py"]