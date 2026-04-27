from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.case import CaseListResponse, CaseOut
from app.services.case_service import get_cases, get_case_by_id
from app.services.report_generator import generate_pdf_report
from fastapi.responses import FileResponse
import os

from app.core.dependencies import get_db, get_current_user

router = APIRouter()

@router.get("/", response_model=CaseListResponse)
async def list_cases(page: int = 1, size: int = 20, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    cases, total = await get_cases(db, current_user, page, size)
    return CaseListResponse(items=cases, total=total, page=page, size=size)

@router.get("/{case_id}", response_model=CaseOut)
async def retrieve_case(case_id: str, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    case = await get_case_by_id(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if current_user.role != "admin" and case.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this case")
    return case

@router.get("/{case_id}/report")
async def download_report(case_id: str, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    case = await get_case_by_id(db, case_id)
    if not case:
         raise HTTPException(status_code=404, detail="Case not found")
    
    if case.status != "completed":
         raise HTTPException(status_code=400, detail="Report only available for completed cases")
         
    if current_user.role != "admin" and case.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this report")
        
    if case.report_path and os.path.exists(case.report_path):
        return FileResponse(case.report_path, filename=f"report_{case_id}.pdf")
        
    # Generate on the fly if not exists
    case_dict = {"id": case.id, "case_type": case.case_type, "verdict": case.verdict, "confidence": case.confidence, "risk_level": case.risk_level}
    new_path = generate_pdf_report(case_dict, current_user.email, current_user.role)
    return FileResponse(new_path, filename=f"report_{case_id}.pdf")

@router.post("/{case_id}/email_report")
async def email_report_endpoint(case_id: str, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    import uuid
    from app.services.email_service import send_report_email
    
    try:
        case_uuid = uuid.UUID(str(case_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Case ID format")
        
    case = await get_case_by_id(db, str(case_uuid))
    if not case:
         raise HTTPException(status_code=404, detail="Case not found")
    
    if case.status != "completed":
         raise HTTPException(status_code=400, detail="Report only available for completed cases")
         
    if current_user.role != "admin" and case.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this case")

    # Get or generate report path
    report_path = case.report_path
    if not report_path or not os.path.exists(report_path):
        case_dict = {"id": case.id, "case_type": case.case_type, "verdict": case.verdict, "confidence": case.confidence, "risk_level": case.risk_level}
        report_path = generate_pdf_report(case_dict, current_user.email, current_user.role)
        
    # Send Email
    subject = f"CyberShield Forensic Report - {case.verdict.upper()} DETECTED"
    body = f"Hello {current_user.full_name or 'Analyst'},\n\nYour neural forensic analysis for case {case_id} has concluded.\n\nVerdict: {case.verdict.upper()}\nConfidence: {case.confidence * 100:.2f}%\nRisk Level: {case.risk_level.upper()}\n\nPlease find the highly detailed PDF report attached to this email for your internal auditing records.\n\nSecurely,\nCyberShield AI System"
    
    sent = send_report_email(current_user.email, subject, body, report_path)
    
    if sent:
        return {"status": "success", "message": f"Report securely emailed to {current_user.email}"}
    else:
        return {"status": "mocked", "message": f"Report generated! (SMTP not configured. Mock email logged to console for {current_user.email})"}
