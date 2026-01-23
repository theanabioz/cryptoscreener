FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем зависимости
COPY engines/indicator-engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем pandas-ta напрямую из GitHub
RUN pip install --no-cache-dir git+https://github.com/twopirllc/pandas-ta.git@master

# Копируем ВЕСЬ бэкенд
COPY . .

ENV PYTHONPATH=/app

CMD ["python3", "engines/indicator-engine/scheduler.py"]