import os
from celery import Celery

broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery_app = Celery(
    "cyber_worker",
    broker=broker_url,
    backend=result_backend,
    include=[
        "worker.tasks.analyze_email",
        "worker.tasks.other_tasks"
    ]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_always_eager=os.getenv("CELERY_TASK_ALWAYS_EAGER", "False").lower() == "true"
)
