from typing import List, Optional
from sqlalchemy.orm import Session
from models import user
from schemas import user as schemas
from app import auth

def create_user(db: Session, userCreate: schemas.UserCreate):
    hashed_password = auth.get_password_hash(userCreate.password)
    db_user = user.User(
        username=userCreate.username,
        email=userCreate.email,
        password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int) -> Optional[user.User]:
    """Fetch a user by its primary key."""
    return db.get(user.User, user_id)

def get_user_by_name(db: Session, name: str) -> Optional[user.User]:
    """Fetch the first user matching the given name."""
    return db.query(user.User).filter(user.User.email == name).first()

def get_user_by_email(db: Session, email: str) -> Optional[user.User]:
    """Fetch the first user matching the given email."""
    return db.query(user.User).filter(user.User.email == email).first()

def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[user.User]:
    """Return a slice of users for paging."""
    return db.query(user.User).offset(skip).limit(limit).all()

def update_user(db: Session, userUpdate: schemas.UserUpdate, user_id: int) -> Optional[user.User]:
    user_obj = get_user(db, user_id)
    if not user_obj:
        return None

    update_data = userUpdate.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user_obj, key, value)

    db.commit()
    db.refresh(user_obj)
    return user_obj


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a User by ID. Returns True if deleted, False if not found."""
    user = get_user(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
