from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.analysis import EmailAnalysisRequest, URLAnalysisRequest, AnalysisResponse
from app.services.analysis_service import create_analysis_case
import sys
import os
import shutil
# Add ml_worker to path for synchronous eager execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../ml_worker")))
from worker.tasks.other_tasks import analyze_image, analyze_video, analyze_audio

from app.core.dependencies import get_db, get_current_user

try:
    from app.services.email_engine import email_engine
except Exception as e:
    email_engine = None

try:
    from app.services.url_engine import url_engine
except Exception as e:
    url_engine = None

router = APIRouter()

@router.post("/email", status_code=200)
async def analyze_email_route(request: EmailAnalysisRequest, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if email_engine is None:
        raise HTTPException(status_code=500, detail="Email Engine failed to load")
    case = await create_analysis_case(db, current_user, "email", "Email Snippet")
    
    result = email_engine.process_email(request.text)
    
    case.status = "completed"
    case.verdict = result["verdict"]
    case.confidence = float(result["confidence"])
    case.risk_level = "high" if result["verdict"] == "threat" else "low"
    await db.commit()

    education = None
    if result["verdict"] == "threat":
        education = {
            "why": f"The neural engine flagged this email as a {result.get('threat_type', 'threat').upper()} threat. It detected common social engineering patterns, urgent calls to action, or malicious URLs. The confidence score of {result['confidence']*100:.1f}% indicates strong algorithmic certainty.",
            "how_to_spot": "Never click links directly from emails claiming urgent account issues. Instead, navigate to the official website manually. Verify the sender's actual email address matches the official domain. When in doubt, contact the organization's official support directly."
        }
    else:
        education = {
            "why": "The algorithmic analysis and heuristic checks found no malicious indicators. The email follows standard formatting, uses reputable domains, and contains no manipulative social engineering language.",
            "how_to_spot": "Even safe emails should be treated with basic caution. Always ensure the sender's address matches their identity and never download unexpected attachments."
        }

    return JSONResponse({
        "case_id": str(case.id),
        "status": "completed",
        "verdict": result["verdict"],
        "confidence": float(result["confidence"]),
        "model1_score": float(result.get("model1_score", 0.0)),
        "model2_score": float(result.get("model2_score", 0.0)),
        "legitimacy_bonus": float(result.get("legitimacy_bonus", 0.0)),
        "reasons": result["reasons"],
        "threat_type": result.get("threat_type", "safe"),
        "xai_data": {
            "top_features": [
                {"token": result.get("threat_type", "safe").upper(), "shap_value": float(result["confidence"]), "position": 0}
            ],
            "education": education
        }
    })

@router.post("/url", status_code=200)
async def analyze_url_route(request: URLAnalysisRequest, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if url_engine is None:
        raise HTTPException(status_code=500, detail="URL Engine failed to load")
    case = await create_analysis_case(db, current_user, "url", str(request.url))
    
    result = url_engine.process_url(str(request.url))
    
    case.status = "completed"
    case.verdict = result["verdict"]
    case.confidence = float(result["confidence"])
    case.risk_level = "high" if result["verdict"] == "threat" else "low"
    await db.commit()

    education = None
    if result["verdict"] == "threat":
        education = {
            "why": f"The analysis flagged this URL as a {result.get('threat_type', 'threat').upper()} threat. It matches patterns of known malicious sites, uses deceptive domain formatting, or was identified by heuristic scans.",
            "how_to_spot": "Always inspect the domain name carefully for misspellings (e.g., 'g00gle.com' instead of 'google.com'). Avoid clicking shortened URLs from untrusted sources."
        }
    else:
        education = {
            "why": "The analysis returned a safe verdict. The domain has a mature registration age, possesses valid SSL certificates, and its neural embedding does not align with known malicious infrastructure.",
            "how_to_spot": "While this URL appears structurally sound, you should still verify that the page content aligns with your expectations before entering any credentials."
        }

    return JSONResponse({
        "case_id": str(case.id),
        "status": "completed",
        "verdict": result["verdict"],
        "confidence": float(result["confidence"]),
        "ml_score": float(result.get("ml_score", 0.0)),
        "heuristic_score": float(result.get("heuristic_score", 0.0)),
        "domain_age_days": result.get("domain_age_days", -1),
        "ssl_valid": result.get("ssl_valid", False),
        "redirect_count": result.get("redirect_count", 0),
        "reasons": result["reasons"],
        "threat_type": result.get("threat_type", "safe"),
        "xai_data": {
            "top_features": [
                {"token": result.get("threat_type", "safe").upper(), "shap_value": float(result["confidence"]), "position": 0}
            ],
            "education": education
        }
    })

@router.post("/image", response_model=AnalysisResponse, status_code=202)
async def analyze_image(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid image type")
    case = await create_analysis_case(db, current_user, "image", file.filename)
    # Save file and dispatch task
    return AnalysisResponse(case_id=case.id, status="pending", message="Image analysis queued")

@router.post("/video", response_model=AnalysisResponse, status_code=202)
async def analyze_video(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if file.content_type != "video/mp4":
        raise HTTPException(status_code=400, detail="Invalid video type. Please upload MP4.")
    case = await create_analysis_case(db, current_user, "video", file.filename)
    return AnalysisResponse(case_id=case.id, status="pending", message="Video analysis queued")

@router.post("/audio", response_model=AnalysisResponse, status_code=202)
async def analyze_audio(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if file.content_type not in ["audio/wav", "audio/mpeg"]:
        raise HTTPException(status_code=400, detail="Invalid audio format")
    case = await create_analysis_case(db, current_user, "audio", file.filename)
    return AnalysisResponse(case_id=case.id, status="pending", message="Audio analysis queued")

@router.post("/full-scan", response_model=AnalysisResponse, status_code=202)
async def analyze_full_scan(
    email_text: Optional[str] = Form(None), 
    url: Optional[str] = Form(None), 
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if not (email_text or url or file):
         raise HTTPException(status_code=400, detail="Provide at least one input for full scan")
    
    case = await create_analysis_case(db, current_user, "full_scan", "Multi-modal scan triggered")
    return AnalysisResponse(case_id=case.id, status="pending", message="Full scan queued")

try:
    from app.services.deepfake_engine import deepfake_engine
    deepfake_import_error = None
except Exception as e:
    deepfake_engine = None
    deepfake_import_error = str(e)

import uuid
from fastapi.responses import JSONResponse

@router.post("/media", status_code=200)
async def analyze_media(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../uploads/temp"))
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")
    
    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
            
        case = await create_analysis_case(db, current_user, "media", file.filename)
        
        # Call the real deepfake model
        if deepfake_engine is None:
            raise HTTPException(status_code=500, detail=f"ML Engine failed to load: {deepfake_import_error}")
        
        mt = "video" if file.content_type.startswith("video/") else "audio" if file.content_type.startswith("audio/") else "image"
        result = deepfake_engine.fused_analysis(temp_path, media_type=mt)
        
        if result.get("verdict") == "invalid":
            raise HTTPException(status_code=400, detail=result.get("error", "Invalid Media File"))
        
        case.status = "completed"
        case.verdict = result["verdict"]
        case.confidence = float(result["confidence"])
        case.risk_level = "high" if result["verdict"] == "deepfake" or result["verdict"] == "threat" else "low"
        await db.commit()

        education = None
        if result["verdict"] == "threat" or result["verdict"] == "suspicious":
            education = {
                "why": f"The multi-modal forensic engine detected synthetic artifacts in this {mt}. The analysis shows high resonance for generative anomalies, such as face-swap artifacts in video/images or synthetic vocoder frequencies in audio.",
                "how_to_spot": "Look for unnatural blurring around the edges of faces, inconsistent lighting or shadows, mismatched skin tones, and unnatural blinking or eye movements in videos. For audio, listen for unnatural breathing, robotic phrasing, or weird background noise suppression."
            }
        else:
            education = {
                "why": f"The forensic analysis did not detect significant generative artifacts. The {mt}'s properties are consistent with an unaltered, real-world recording.",
                "how_to_spot": "Continue to be mindful of context. Genuine media can still be used deceptively if it is presented alongside false information."
            }

        return JSONResponse({
            "case_id": str(case.id),
            "status": "completed",
            "verdict": result["verdict"],
            "threat_type": result.get("threat_type", "real"),
            "is_phishing": result["verdict"] in ["threat", "suspicious"],
            "confidence": float(result["confidence"]),
            "model_label": result.get("label", ""),
            "deepfake_score": float(result.get("deepfake_score", 0.0)),
            "sdxl_score": float(result.get("sdxl_score", 0.0)),
            "gemini_score": float(result.get("gemini_score", 0.0)),
            "ai_generated_score": float(result.get("ai_generated_score", 0.0)),
            "face_detected": bool(result.get("face_detected", False)),
            "reasons": result.get("reasons", []),
            "xai_data": {
                "top_features": [
                    {"token": "Deepfake Analysis", "shap_value": float(result.get("deepfake_score", 0.0)), "position": 0},
                    {"token": "SDXL Generation Analysis", "shap_value": float(result.get("sdxl_score", 0.0)), "position": 1},
                    {"token": "Gemini Generation Analysis", "shap_value": float(result.get("gemini_score", 0.0)), "position": 2},
                ],
                "education": education
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
