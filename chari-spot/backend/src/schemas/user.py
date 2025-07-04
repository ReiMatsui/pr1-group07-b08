from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


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

    model_config = ConfigDict(from_attributes = True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None
