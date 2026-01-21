import pandas as pd
import glob
import os
import psycopg2
from sqlalchemy import create_engine
import time
from tqdm import tqdm

# Настройки подключения
DB_URL = "postgresql://postgres:password@timescaledb:5432/postgres"
DATA_DIR = "/data/raw_parquet"

def ingest():
    files = glob.glob(os.path.join(DATA_DIR, "*.parquet"))
    if not files:
        print(f"No parquet files found in {DATA_DIR}!")
        return
        
    print(f"Found {len(files)} files to ingest.")
    
    # Ждем, пока база поднимется
    engine = None
    for i in range(10):
        try:
            engine = create_engine(DB_URL)
            engine.connect()
            break
        except Exception as e:
            print(f"Waiting for DB... ({e})")
            time.sleep(3)

    if not engine:
        print("Could not connect to database. Exiting.")
        return

    # Используем tqdm для прогресс-бара
    pbar = tqdm(files, desc="Ingesting coins", unit="coin")
    
    for file_path in pbar:
        symbol = os.path.basename(file_path).replace('.parquet', '')
        # Приводим к стандарту BTC/USDT
        db_symbol = symbol.replace('USDT', '/USDT')
        
        pbar.set_postfix({"symbol": db_symbol})
        
        try:
            df = pd.read_parquet(file_path)
            df['symbol'] = db_symbol
            
            # Сохраняем в БД
            df.to_sql('candles', engine, if_exists='append', index=False, chunksize=10000)
            
        except Exception as e:
            print(f"\nError ingesting {symbol}: {e}")

    print("\n✅ Ingestion complete!")

if __name__ == "__main__":
    ingest()
