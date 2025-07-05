
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
import pytz
import logging

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Timezone
IST = pytz.timezone("Asia/Kolkata")

# Database setup (switch to sqlite:///:memory: for pure in-memory)
DATABASE_URL = "sqlite:///bookings.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Models
class FitnessClass(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    datetime = Column(DateTime)
    instructor = Column(String)
    available_slots = Column(Integer)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer)
    class_name = Column(String)
    client_name = Column(String)
    client_email = Column(String)
    datetime = Column(DateTime)

Base.metadata.create_all(bind=engine)

# Populate sample classes (only once)
def populate_classes():
    db = SessionLocal()
    if db.query(FitnessClass).count() == 0:
        db.add_all([
            FitnessClass(id=1, name="Yoga", datetime=IST.localize(datetime(2025, 7, 6, 18, 0)), instructor="rajeshwari", available_slots=10),
            FitnessClass(id=2, name="HIIT", datetime=IST.localize(datetime(2025, 7, 6, 18, 0)), instructor="shashi", available_slots=8),
            FitnessClass(id=3, name="zumba", datetime=IST.localize(datetime(2025, 7, 6, 18, 0)), instructor="hiremath", available_slots=9),
            FitnessClass(id=4, name="gym", datetime=IST.localize(datetime(2025, 7, 9, 18, 0)), instructor="onimath", available_slots=9)
        ])
        db.commit()
    db.close()

populate_classes()


class ClassOut(BaseModel):
    id: int
    name: str
    datetime: str
    instructor: str
    available_slots: int

class BookingIn(BaseModel):
    class_id: int = Field(..., gt=0, description="Must be a positive integer")
    client_name: str = Field(..., min_length=2, description="Name must have at least 2 characters")
    client_email: EmailStr

class BookingOut(BaseModel):
    class_id: int
    class_name: str
    client_name: str
    client_email: EmailStr
    datetime: str

# Utility
def to_timezone(dt: datetime, tz: str) -> str:
    try:
        target = pytz.timezone(tz)
        return dt.astimezone(target).isoformat()
    except Exception:
        return dt.isoformat()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Fit Studio Booking API. Visit /docs for API documentation."}

@app.get("/classes", response_model=List[ClassOut])
def get_classes(tz: Optional[str] = Query("Asia/Kolkata")):
    db = SessionLocal()
    now = datetime.now(IST)
    results = db.query(FitnessClass).filter(FitnessClass.datetime > now).all()
    db.close()
    return [
        {
            "id": c.id,
            "name": c.name,
            "datetime": to_timezone(c.datetime, tz),
            "instructor": c.instructor,
            "available_slots": c.available_slots
        }
        for c in results
    ]

@app.post("/book", response_model=BookingOut)
def book_class(data: BookingIn):
    db = SessionLocal()
    cls = db.query(FitnessClass).filter(FitnessClass.id == data.class_id).first()
    if not cls:
        db.close()
        raise HTTPException(status_code=404, detail="Class not found")

    if cls.available_slots <= 0:
        db.close()
        raise HTTPException(status_code=400, detail="No slots available")

    cls.available_slots -= 1
    booking = Booking(
        class_id=cls.id,
        class_name=cls.name,
        client_name=data.client_name,
        client_email=data.client_email,
        datetime=cls.datetime
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    response = {
    "class_id": booking.class_id,
    "class_name": booking.class_name,
    "client_name": booking.client_name,
    "client_email": booking.client_email,
    "datetime": booking.datetime.isoformat()
    }

   
    db.close()
    return response
@app.get("/bookings", response_model=List[BookingOut])
def get_bookings(email: EmailStr = Query(...)):
    db = SessionLocal()
    results = db.query(Booking).filter(Booking.client_email == email).all()
    db.close()
    return [
        {
            "class_id": b.class_id,
            "class_name": b.class_name,
            "client_name": b.client_name,
            "client_email": b.client_email,
            "datetime": b.datetime.isoformat()
        }
        for b in results
    ]
