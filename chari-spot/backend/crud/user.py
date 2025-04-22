from typing import List, Optional
from sqlalchemy.orm import Session
from models import user
from schemas import user as schemas

def create_user(db: Session, userCreate: schemas.UserCreate):
    db_user = user.User(
        username=userCreate.username,
        email=userCreate.email,
        password=userCreate.password
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

def update_user(db: Session, userUpdate: schemas.UserUpdate) -> Optional[user.User]:
    """Update fields on a User. Returns the updated User, or None if not found."""
    user = get_user(db, userUpdate.id)
    if not user:
        return None
    if userUpdate.username is not None:
        user.username = userUpdate.username
    if userUpdate.email is not None:
        user.email = userUpdate.email
    if userUpdate.password is not None:
        user.password = userUpdate.password
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> bool:
    """Delete a User by ID. Returns True if deleted, False if not found."""
    user = get_user(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
