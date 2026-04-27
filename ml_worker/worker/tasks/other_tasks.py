from worker.celery_app import celery_app
from worker.tasks.analyze_email import analyze_email
from models.url_model import MockURLModel
from models.image_model import MockImageModel
from models.video_model import MockVideoModel
from models.audio_model import MockAudioModel
from utils.db import update_case_status, insert_modality_result
from utils.redis_pub import publish_update
from worker.tasks.task_utils import compute_risk_level

def create_task_template(task_name: str, model_cls, modality: str):
    @celery_app.task(bind=True, max_retries=3, name=task_name)
    def generic_task(self, case_id: str, input_data: str):
        try:
            publish_update(case_id, {"event": "started", "status": "processing", "progress": 10})
            update_case_status(case_id, "processing")
            
            publish_update(case_id, {"event": "inference", "progress": 50})
            model = model_cls()
            result = model.predict(input_data)
            
            publish_update(case_id, {"event": "xai", "progress": 80})
            insert_modality_result(case_id, modality, result["verdict"], result["confidence"], result["xai_data"], result["processing_time_ms"])
            
            risk = compute_risk_level(result["confidence"], result["verdict"])
            update_case_status(case_id, "completed", result["verdict"], result["confidence"], risk)
            
            publish_update(case_id, {"event": "completed", "progress": 100, "verdict": result["verdict"], "confidence": result["confidence"]})
            return result
        except Exception as exc:
            update_case_status(case_id, "failed")
            publish_update(case_id, {"event": "failed", "progress": 0})
            raise self.retry(exc=exc, countdown=5)
    return generic_task

analyze_url = create_task_template("worker.tasks.analyze_url", MockURLModel, "url")
analyze_image = create_task_template("worker.tasks.analyze_image", MockImageModel, "image")
analyze_video = create_task_template("worker.tasks.analyze_video", MockVideoModel, "video")
analyze_audio = create_task_template("worker.tasks.analyze_audio", MockAudioModel, "audio")

@celery_app.task(bind=True, max_retries=3)
def full_scan(self, case_id: str, inputs_dict: dict):
    # Not fully implemented - sequential dispatch simulation
    update_case_status(case_id, "completed", "phishing", 0.99, "critical")
    publish_update(case_id, {"event": "completed", "progress": 100, "verdict": "phishing", "confidence": 0.99})
    return {"status": "success"}
