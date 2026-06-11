from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/guardians", tags=["guardians"])

# Mock guardian data
GUARDIANS = [
    {"id": "G001", "name": "Thabo Nkosi", "status": "on_patrol", "phone": "+27721234567", "avatar": "TN"},
    {"id": "G002", "name": "Nomsa Mthethwa", "status": "gate", "phone": "+27721234568", "avatar": "NM"},
    {"id": "G003", "name": "Sipho Dlamini", "status": "responding", "phone": "+27721234569", "avatar": "SD"},
    {"id": "G004", "name": "Rapid Response", "status": "mobile", "phone": "0800123456", "avatar": "RR"},
]

@router.get("/")
async def get_guardians(user=Depends(get_current_user)):
    """Get all active guardians"""
    return GUARDIANS

@router.put("/{guardian_id}/status")
async def update_guardian_status(guardian_id: str, status: str, user=Depends(get_current_user)):
    """Update guardian patrol status"""
    for g in GUARDIANS:
        if g["id"] == guardian_id:
            g["status"] = status
            return {"success": True, "guardian": g}
    raise HTTPException(status_code=404, detail="Guardian not found")

@router.post("/share-location")
async def share_location(location: dict, user=Depends(get_current_user)):
    """Receive live location from user (for guardian dispatch)"""
    # Store in Firestore or Redis for real-time tracking
    return {"success": True, "message": "Location shared with guardians"}
