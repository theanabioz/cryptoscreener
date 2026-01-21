#!/bin/bash

# Останавливаем при любой ошибке
set -e

echo "🚀 Starting Production Deployment..."

# 1. Проверяем файл .env
if [ ! -f .env ]; then
    echo "⚠️ .env file not found! Creating default one..."
    echo "POSTGRES_USER=postgres" > .env
    echo "POSTGRES_PASSWORD=password" >> .env
    echo "POSTGRES_DB=postgres" >> .env
    echo "POSTGRES_HOST=timescaledb" >> .env
    echo "POSTGRES_PORT=5432" >> .env
fi

# Загружаем переменные окружения
export $(grep -v '^#' .env | xargs)

# 2. Останавливаем старые контейнеры
echo "🛑 Stopping containers..."
docker compose down --remove-orphans

# 3. Запускаем только базу данных
echo "🐘 Starting Database..."
docker compose up -d timescaledb

# 4. Ждем, пока база станет здоровой (Healthcheck)
echo "⏳ Waiting for Database to be ready..."
until docker inspect --format "{{json .State.Health.Status}}" crypto_db | grep -q "healthy"; do
    echo -n "."
    sleep 2
done
echo "✅ Database is Healthy!"

# 5. СИНХРОНИЗАЦИЯ ПАРОЛЯ (Критический этап)
# Это гарантирует, что пароль в конфиге совпадает с паролем внутри базы
echo "🔐 Syncing Database Password..."
docker exec crypto_db psql -U $POSTGRES_USER -c "ALTER USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';"

# 6. Запускаем всё остальное с пересборкой
echo "🏗 Building and Starting Services..."
docker compose up -d --build

# 7. Финальная проверка
echo "🔍 Verifying API..."
sleep 5
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/coins)

if [ "$HTTP_CODE" -eq 200 ]; then
    echo "✅ DEPLOYMENT SUCCESSFUL! API is responding (200 OK)."
    echo "📊 Coin List:"
    curl -s http://localhost:8000/api/coins | head -c 100
    echo "..."
else
    echo "❌ DEPLOYMENT FAILED. API returned status $HTTP_CODE"
    docker logs crypto_api --tail 20
    exit 1
fi
