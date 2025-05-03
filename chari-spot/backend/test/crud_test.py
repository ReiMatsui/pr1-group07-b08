import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base
from crud.user import (
    create_user, get_user, get_user_by_name, get_user_by_email,
    list_users, update_user, delete_user
)
from crud.parking import (
    create_parking, get_parking, get_parkings,
    update_slot, delete_slot
)
from schemas.user import UserCreate, UserUpdate
from schemas.parking import ParkingCreate, ParkingUpdate


@ pytest.fixture
def db_session():
    """
    Create a new database session for testing, using in-memory SQLite.
    """
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    # create all tables
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# Tests for User CRUD operations

def test_user_crud(db_session):
    # Create a new user
    user_in = UserCreate(
        username="testuser",
        email="test@example.com",
        password="secret"
    )
    user = create_user(db_session, user_in)

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"

    # Read user by ID
    fetched = get_user(db_session, user.id)
    assert fetched.id == user.id

    # Read user by name (email field)
    by_name = get_user_by_name(db_session, "test@example.com")
    assert by_name.id == user.id

    # Read user by email
    by_email = get_user_by_email(db_session, "test@example.com")
    assert by_email.id == user.id

    # List users
    users = list_users(db_session)
    assert len(users) == 1

    # Update user
    update_data = UserUpdate(
        id=user.id,
        username="updated_user"
    )
    updated = update_user(db_session, update_data)
    assert updated.username == "updated_user"

    # Delete user
    result = delete_user(db_session, user.id)
    assert result is True
    assert get_user(db_session, user.id) is None

    # Deleting non-existent user returns False
    assert delete_user(db_session, 999) is False


# Tests for Parking CRUD operations

def test_parking_crud(db_session):
    # First, create an owner user
    owner_in = UserCreate(
        username="owner",
        email="owner@example.com",
        password="secret"
    )
    owner = create_user(db_session, owner_in)

    # Create a new parking slot
    parking_in = ParkingCreate(
        name="Lot A",
        address="123 Main St",
        latitude=12.34,
        longitude=56.78,
        avail_slots=5,
        total_slots=10,
        owner_id=owner.id
    )
    parking = create_parking(db_session, parking_in)

    assert parking.id is not None
    assert parking.name == "Lot A"

    # Read parking by ID
    fetched = get_parking(db_session, parking.id)
    assert fetched.id == parking.id

    # Read list of parkings
    parkings = get_parkings(db_session)
    assert len(parkings) == 1

    # Update parking slot
    update_parking = ParkingUpdate(
        id=parking.id,
        name="Lot B",
        avail_slots=8
    )
    updated = update_slot(db_session, update_parking)
    assert updated.name == "Lot B"
    assert updated.avail_slots == 8

    # Delete parking slot
    deleted = delete_slot(db_session, parking.id)
    assert deleted is True
    assert get_parking(db_session, parking.id) is None

    # Deleting non-existent slot returns False
    assert delete_slot(db_session, 999) is False
