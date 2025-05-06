from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# SQLite Local Database URL
SQLALCHEMY_DATABASE_URL = "sqlite:////Users/fukuokaryousuke/pr1-group07-b08/chari-spot/backend/chari-spot.db"

# create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}  # SQLite needs check_same_thread=False
)

# create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create ORM
Base = declarative_base()

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()