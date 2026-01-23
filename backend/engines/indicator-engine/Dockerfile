FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей + wget для скачивания TA-Lib
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Сборка и установка TA-Lib (C library)
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && rm -rf ta-lib*

# Копируем requirements
COPY engines/indicator-engine/requirements.txt .
# Устанавливаем Python-обертку TA-Lib вместе с остальными
RUN pip install --no-cache-dir TA-Lib
RUN pip install --no-cache-dir -r requirements.txt

# Копируем и устанавливаем локальный pandas-ta
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