from worker.celery_app import celery_app
from models.email_model import MockEmailModel
from utils.db import update_case_status, insert_modality_result
from utils.redis_pub import publish_update
from worker.tasks.task_utils import compute_risk_level

@celery_app.task(bind=True, max_retries=3)
def analyze_email(self, case_id: str, text: str):
    try:
        publish_update(case_id, {"event": "started", "status": "processing", "progress": 10})
        update_case_status(case_id, "processing")
        
        publish_update(case_id, {"event": "inference", "progress": 50})
        model = MockEmailModel()
        result = model.predict(text)
        
        publish_update(case_id, {"event": "xai", "progress": 80})
        insert_modality_result(case_id, "email", result["verdict"], result["confidence"], result["xai_data"], result["processing_time_ms"])
        
        risk = compute_risk_level(result["confidence"], result["verdict"])
        update_case_status(case_id, "completed", result["verdict"], result["confidence"], risk)
        
        publish_update(case_id, {"event": "completed", "progress": 100, "verdict": result["verdict"], "confidence": result["confidence"]})
        return result
    except Exception as exc:
        update_case_status(case_id, "failed")
        publish_update(case_id, {"event": "failed", "progress": 0})
        raise self.retry(exc=exc, countdown=5)
