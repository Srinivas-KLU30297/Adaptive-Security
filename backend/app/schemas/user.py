from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "viewer"

class UserUpdate(BaseModel):
    is_active: Optional[bool] = None
    role: Optional[str] = None
