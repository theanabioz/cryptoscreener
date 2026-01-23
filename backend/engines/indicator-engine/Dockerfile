FROM python:3.10-slim

WORKDIR /app

# 1. System Dependencies (TA-Lib needs build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. Build TA-Lib C Library
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && rm -rf ta-lib*

# 3. Install Python Dependencies
COPY engines/indicator-engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy Application Code
# We are building from 'backend/' context, so we can copy 'common'
COPY common /app/common
COPY engines/indicator-engine /app/engines/indicator-engine

# 5. Environment Variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 6. Default Command (can be overridden by docker-compose)
CMD ["python3", "engines/indicator-engine/main.py"]