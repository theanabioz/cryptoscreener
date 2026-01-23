-- Включаем необходимые расширения (обычно они уже включены в образе Timescale, но на всякий случай)
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 1. Создаем таблицу свечей
-- Мы используем DOUBLE PRECISION для цен, так как для крипты (0.00000123) это точнее и быстрее, чем NUMERIC
CREATE TABLE IF NOT EXISTS candles (
    time TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume DOUBLE PRECISION,
    -- Первичный ключ в Timescale всегда включает time
    PRIMARY KEY (time, symbol)
);

-- 2. Превращаем в гипертаблицу (разбиение по времени, по умолчанию chunk = 7 дней)
SELECT create_hypertable('candles', 'time', if_not_exists => TRUE);

-- 3. Настраиваем СЖАТИЕ (Compression)
-- Это магия Timescale. Мы сжимаем данные по символу.
ALTER TABLE candles SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol',
    timescaledb.compress_orderby = 'time DESC'
);

-- 4. Политика сжатия: сжимать данные старше 3 дней
-- (Свежие данные остаются "горячими" для быстрого обновления, старые ужимаются)
SELECT add_compression_policy('candles', INTERVAL '3 days');

-- 5. (Опционально) Политика удаления: хранить 2 года (как мы обсуждали)
SELECT add_retention_policy('candles', INTERVAL '2 years');
