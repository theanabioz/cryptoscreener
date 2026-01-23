CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS candles (
    time TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume DOUBLE PRECISION,
    UNIQUE (time, symbol)
);

-- Convert to hypertable
SELECT create_hypertable('candles', 'time', chunk_time_interval => INTERVAL '1 week', if_not_exists => TRUE);

-- Status Table (Stateful Engine Output)
CREATE TABLE IF NOT EXISTS coin_status (
    symbol TEXT PRIMARY KEY,
    current_price DOUBLE PRECISION,
    volume_24h DOUBLE PRECISION,
    price_change_24h DOUBLE PRECISION,
    indicators_1m JSONB DEFAULT '{}',
    indicators_5m JSONB DEFAULT '{}',
    indicators_15m JSONB DEFAULT '{}',
    indicators_1h JSONB DEFAULT '{}',
    indicators_4h JSONB DEFAULT '{}',
    indicators_1d JSONB DEFAULT '{}',
    sparkline_in_7d JSONB DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Metadata
CREATE TABLE IF NOT EXISTS coins_meta (
    symbol TEXT PRIMARY KEY,
    name TEXT,
    full_name TEXT,
    rank INT,
    is_active BOOLEAN DEFAULT TRUE,
    added_at TIMESTAMPTZ DEFAULT NOW()
);
