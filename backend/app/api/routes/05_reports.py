from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])

class ReportCreate(BaseModel):
    category: str
    location: str
    description: str
    videoUrl: Optional[str] = None
    anonymous: bool = True

# In-memory storage (replace with Firestore)
reports_db = []

@router.post("/")
async def create_report(report: ReportCreate, user=Depends(get_current_user)):
    """Create anonymous safety report"""
    report_data = {
        "reportId": f"rpt_{len(reports_db)+1}",
        "userId": None if report.anonymous else user.get("userId"),
        "category": report.category,
        "location": report.location,
        "description": report.description,
        "videoUrl": report.videoUrl,
        "anonymous": report.anonymous,
        "timestamp": datetime.now().isoformat(),
        "status": "submitted"
    }
    reports_db.append(report_data)
    return {"success": True, "reportId": report_data["reportId"]}

@router.get("/")
async def get_reports(limit: int = 20, user=Depends(get_current_user)):
    """Get reports (admin only in production)"""
    return reports_db[-limit:]
