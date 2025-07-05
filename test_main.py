import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import pytz

from main import app, Base, engine, SessionLocal, FitnessClass

client = TestClient(app)
IST = pytz.timezone("Asia/Kolkata")


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    # Clear and recreate DB tables before each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    db.add_all([
        FitnessClass(
            id=1,
            name="Yoga",
            datetime=IST.localize(datetime(2025, 7, 10, 10, 0)),
            instructor="A",
            available_slots=5
        ),
        FitnessClass(
            id=2,
            name="HIIT",
            datetime=IST.localize(datetime(2025, 7, 11, 12, 0)),
            instructor="B",
            available_slots=0  # fully booked
        )
    ])
    db.commit()
    db.close()
    yield


def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert "message" in res.json()


def test_get_classes():
    res = client.get("/classes")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] in ["Yoga", "HIIT"]


def test_successful_booking():
    res = client.post("/book", json={
        "class_id": 1,
        "client_name": "rama",
        "client_email": "rama@example.com"
    })
    assert res.status_code == 200
    booking = res.json()
    assert booking["class_id"] == 1
    assert booking["client_name"] == "rama"


def test_booking_class_not_found():
    res = client.post("/book", json={
        "class_id":14,
        "client_name": "rama1",
        "client_email": "rama1@example.com"
    })
    assert res.status_code == 404
    assert res.json()["detail"] == "Class not found"


def test_booking_no_slots():
    res = client.post("/book", json={
        "class_id": 2,  # zero slots
        "client_name": "NoSlot",
        "client_email": "noslot@example.com"
    })
    assert res.status_code == 400
    assert res.json()["detail"] == "No slots available"


def test_booking_invalid_email():
    res = client.post("/book", json={
        "class_id": 1,
        "client_name": "Invalid",
        "client_email": "not-an-email"
    })
    assert res.status_code == 422  # validation error


def test_booking_missing_fields():
    res = client.post("/book", json={
        "class_id": 1,
        "client_email": "missing@example.com"
    })
    assert res.status_code == 422  # missing client_name


def test_get_bookings_by_email():
    # First create a booking
    client.post("/book", json={
        "class_id": 1,
        "client_name": "shashi",
        "client_email": "shashi@example.com"
    })

    # Then retrieve it
    res = client.get("/bookings", params={"email": "shashi@example.com"})
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert data[0]["client_name"] == "shashi"


def test_get_bookings_invalid_email():
    res = client.get("/bookings", params={"email": "invalid-email"})
    assert res.status_code == 422
