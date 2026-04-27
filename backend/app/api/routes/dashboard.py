from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.dependencies import get_db, get_current_user
from app.models.case import Case

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    
    # Base query for cases based on user role
    base_query = select(Case)
    if current_user.role != "admin":
        base_query = base_query.where(Case.user_id == current_user.id)
        
    # Total scans
    stmt_total = select(func.count(Case.id))
    if current_user.role != "admin":
        stmt_total = stmt_total.where(Case.user_id == current_user.id)
    total_scans = await db.scalar(stmt_total) or 0
    
    # Verdicts and types
    stmt_types = select(Case.case_type, Case.verdict, func.count(Case.id)).group_by(Case.case_type, Case.verdict)
    if current_user.role != "admin":
        stmt_types = stmt_types.where(Case.user_id == current_user.id)
    types_res = await db.execute(stmt_types)
    
    phishing_count = 0
    deepfake_count = 0
    verdicts_dict = {}
    
    for case_type, verdict, count in types_res.all():
        if verdict:
            verdicts_dict[verdict] = verdicts_dict.get(verdict, 0) + count
            if verdict in ["threat", "suspicious", "phishing", "deepfake", "deepfake_video", "deepfake_audio", "ai_generated", "ai_generated_video"]:
                if case_type in ["media", "image", "video", "audio"]:
                    deepfake_count += count
                else:
                    phishing_count += count
    
    # Average confidence
    stmt_conf = select(func.avg(Case.confidence))
    if current_user.role != "admin":
        stmt_conf = stmt_conf.where(Case.user_id == current_user.id)
    avg_conf = await db.scalar(stmt_conf) or 0.0

    return {
        "total_scans": total_scans,
        "phishing_detected": phishing_count,
        "deepfakes_detected": deepfake_count,
        "scans_today": total_scans, # Simplified to total for now
        "avg_confidence": float(avg_conf),
        "risk_distribution": {"low": 0, "medium": 0, "high": 0, "critical": phishing_count},
        "weekly_scan_volume": [{"date": "Mon", "count": 0}, {"date": "Tue", "count": total_scans}],
        "verdict_distribution": [{"verdict": k, "count": v} for k, v in verdicts_dict.items() if k is not None],
        "modality_usage": [{"modality": "email", "count": 0}, {"modality": "image", "count": 0}]
    }
