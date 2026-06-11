from fastapi import APIRouter, Depends
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/ads", tags=["ads"])

# Rotating ads for free tier users
ADS = [
    {"id": "ad_1", "image": "https://i.postimg.cc/7Zr4y4Jz/boxer-sample-image-removebg-preview.png", "link": "https://www.boxer.co.za", "alt": "Boxer"},
    {"id": "ad_2", "image": "https://i.postimg.cc/T3ytnBqN/KD-LOGO-IMAGE-removebg-preview.png", "link": "https://www.kd.co.za", "alt": "KD"},
]

@router.get("/")
async def get_ads(user=Depends(get_current_user)):
    """Get rotating advertisements for free tier"""
    # Simple rotation based on timestamp
    import time
    idx = int(time.time()) % len(ADS)
    return {"ad": ADS[idx]}
