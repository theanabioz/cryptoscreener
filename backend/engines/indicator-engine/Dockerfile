FROM python:3.12-slim

WORKDIR /app

# 1. Системные зависимости (build-essential нужен для компиляции TA-Lib)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. Сборка и установка C-библиотеки TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && rm -rf ta-lib*

# 3. Установка Python зависимостей
COPY engines/indicator-engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Установка вашей версии pandas-ta из архива
COPY ./pandas_ta-0.4.71b0.tar.gz /tmp/
RUN pip install --no-cache-dir /tmp/pandas_ta-0.4.71b0.tar.gz && rm /tmp/pandas_ta-0.4.71b0.tar.gz

# 5. Копирование кода
COPY . .

# Окружение
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python3", "engines/indicator-engine/scheduler.py"]
