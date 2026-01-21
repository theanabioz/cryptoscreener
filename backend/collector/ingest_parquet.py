import pandas as pd
import glob
import os
import psycopg2
from sqlalchemy import create_engine
import time

# Настройки подключения
DB_URL = "postgresql://postgres:password@timescaledb:5432/screener"
DATA_DIR = "/data/raw_parquet"

def ingest():
    files = glob.glob(os.path.join(DATA_DIR, "*.parquet"))
    print(f"Found {len(files)} files to ingest.")
    
    # Ждем, пока база поднимется
    engine = None
    for i in range(10):
        try:
            engine = create_engine(DB_URL)
            engine.connect()
            break
        except:
            print("Waiting for DB...")
            time.sleep(3)

    for i, file_path in enumerate(files):
        symbol = os.path.basename(file_path).replace('.parquet', '')
        # В БД у нас обычно символ с косой чертой или в оригинальном виде. 
        # Если в имени файла BTCUSDT, в БД положим BTC/USDT (или оставим как есть)
        # Давайте приведем к единому стандарту: добавим слэш перед USDT
        db_symbol = symbol.replace('USDT', '/USDT')
        
        print(f"[{i+1}/{len(files)}] Ingesting {db_symbol}...")
        
        try:
            df = pd.read_parquet(file_path)
            # Переименовываем колонки под схему БД
            # Схема: time, symbol, open, high, low, close, volume
            df['symbol'] = db_symbol
            
            # Сохраняем в БД используя быстрый метод
            # Мы используем method='multi' или просто to_sql с чанками
            df.to_sql('candles', engine, if_exists='append', index=False, chunksize=10000)
            
        except Exception as e:
            print(f"Error ingesting {symbol}: {e}")

    print("✅ Ingestion complete!")

if __name__ == "__main__":
    ingest()
