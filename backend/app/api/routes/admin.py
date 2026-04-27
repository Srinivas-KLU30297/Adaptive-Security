from fastapi import APIRouter
from app.schemas.user import UserCreate

router = APIRouter()

@router.get("/users")
async def list_users():
    return []

@router.post("/users")
async def create_user(user: UserCreate):
    return {"message": "User created"}

@router.patch("/users/{id}")
async def update_user(id: str):
    return {"message": f"User {id} updated"}

@router.get("/system")
async def system_health():
    return {
        "db_status": "online",
        "redis_status": "online",
        "pending_tasks": 0,
        "ml_worker_status": "online",
        "total_users": 3,
        "disk_usage_mb": 420
    }
