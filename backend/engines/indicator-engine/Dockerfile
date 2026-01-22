FROM python:3.10-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости (они теперь общие для всех движков)
COPY engines/indicator-engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uvicorn[standard] websockets ccxt[pro]

# Копируем ВЕСЬ бэкенд в контейнер
COPY . .

# По умолчанию CMD будет переопределяться в docker-compose
CMD ["python3", "engines/indicator-engine/scheduler.py"]
