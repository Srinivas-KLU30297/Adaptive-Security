import redis
import json
import os
from datetime import datetime

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_client = redis.from_url(redis_url)

def publish_update(case_id: str, message_dict: dict):
    channel = f"case_updates:{case_id}"
    message_dict["timestamp"] = datetime.utcnow().isoformat()
    if "case_id" not in message_dict:
        message_dict["case_id"] = case_id
    
    redis_client.publish(channel, json.dumps(message_dict))
