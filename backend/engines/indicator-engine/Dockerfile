FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements
COPY engines/indicator-engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем архив библиотеки (если он есть) и устанавливаем
# Мы используем wildcard *, чтобы билд не падал, если файла временно нет
COPY ./pandas_ta-0.4.71b0.tar.gz* /tmp/
RUN if [ -f /tmp/pandas_ta-0.4.71b0.tar.gz ]; then \
        pip install --no-cache-dir /tmp/pandas_ta-0.4.71b0.tar.gz; \
    else \
        pip install --no-cache-dir pandas-ta; \
    fi

# Копируем ВЕСЬ бэкенд
COPY . .

ENV PYTHONPATH=/app

CMD ["python3", "engines/indicator-engine/scheduler.py"]
