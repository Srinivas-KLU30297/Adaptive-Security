from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import SessionLocal
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, UserOut
from app.schemas.user import UserCreate
from app.services.auth_service import authenticate_user, register_user
from app.core.security import create_access_token, decode_token
from app.core.config import settings

from app.core.dependencies import get_db

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await authenticate_user(db, login_data)

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await register_user(db, user_data)

@router.post("/refresh")
async def refresh(refresh_data: RefreshRequest):
    try:
        payload = decode_token(refresh_data.refresh_token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        new_token = create_access_token(data={"sub": user_id})
        return {"access_token": new_token, "token_type": "bearer"}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/logout")
async def logout():
    # Typically would blacklist token in redis
    return {"message": "Logged out successfully"}
