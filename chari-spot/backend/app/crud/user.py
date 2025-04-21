from sqlalchemy.orm import Session
from app.models import user as models
from app.schemas import user as schemas



# 创建用户
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
