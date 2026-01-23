FROM python:3.10-slim
WORKDIR /app
RUN pip install fastapi uvicorn[standard] asyncpg redis python-dotenv
COPY common /app/common
COPY services/api /app/services/api
ENV PYTHONPATH=/app
CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]