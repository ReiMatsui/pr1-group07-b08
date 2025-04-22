from pydantic import BaseModel, EmailStr

# 用户注册请求体
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str  # 用户提交的明文密码

# 注册成功后返回的响应体
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True  # 让 Pydantic 支持从 ORM 对象读取数据

