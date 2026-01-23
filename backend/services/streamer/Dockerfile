FROM python:3.12-slim
WORKDIR /app
RUN pip install websockets asyncpg redis python-dotenv
COPY common /app/common
COPY services/streamer /app/services/streamer
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
CMD ["python", "services/streamer/main.py"]