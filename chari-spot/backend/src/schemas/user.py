from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str  # 用户提交的明文密码

class UserUpdate(BaseModel):
    id: int
    username: Optional[str]     = None
    email:    Optional[EmailStr] = None
    password: Optional[str]     = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True  # 让 Pydantic 支持从 ORM 对象读取数据

