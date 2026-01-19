from fastapi import APIRouter, HTTPException
from app.services.screener_service import ScreenerService

router = APIRouter()
screener_service = ScreenerService()

@router.get("/coins")
async def get_coins(limit: int = 50):
    try:
        data = screener_service.get_crypto_screener(limit=limit)
        return data
    except Exception as e:
        print(f"Error fetching screener data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
