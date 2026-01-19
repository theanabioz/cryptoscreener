from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Crypto Screener Core"
    BINANCE_WS_URL: str = "wss://stream.binance.com:9443/ws"
    
    # Список символов, за которыми следим (для начала топ-50, потом сделаем динамически)
    # Но Binance !miniTicker@arr дает ВСЕ тикеры сразу, так что нам даже список не нужен для сокета.
    
    class Config:
        env_file = ".env"

settings = Settings()
