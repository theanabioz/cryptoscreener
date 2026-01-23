FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev wget git ca-certificates && rm -rf /var/lib/apt/lists/*

# TA-Lib C
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && rm -rf ta-lib*

# Install Dependencies
RUN pip install pandas numpy asyncpg redis uvloop python-dotenv TA-Lib

# Install Local Pandas TA
COPY pandas_ta-0.4.71b0.tar.gz /tmp/
RUN pip install /tmp/pandas_ta-0.4.71b0.tar.gz && rm /tmp/pandas_ta-0.4.71b0.tar.gz

COPY common /app/common
COPY services/indicator_engine /app/services/indicator_engine
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
CMD ["python", "services/indicator_engine/main.py"]