Fitness Studio Booking API

GitHub Repository: https://github.com/hiremathrajeshwari/https---github.com-hiremathrajeshwari-fitness_studio


Setup Instructions

 1. Clone the Repository

git clone https://github.com/hiremathrajeshwari/https---github.com-hiremathrajeshwari-fitness_studio.git

2. Install Dependencies

pip install fastapi uvicorn sqlalchemy pydantic pytz


3. Run the API Server

uvicorn main:app --reload

--------------------Sample Data----------------------------------------

On startup, the app populates the database with four fitness classes:

| ID | Name  | Instructor | DateTime (IST)         | Slots |
| -- | ----- | ---------- | ---------------------- | ----- |
| 1  | Yoga  | Rajeshwari | July 6, 2025 - 6:00 PM | 10    |
| 2  | HIIT  | Shashi     | July 6, 2025 - 6:00 PM | 8     |
| 3  | Zumba | Hiremath   | July 6, 2025 - 6:00 PM | 9     |
| 4  | Gym   | Onimath    | July 9, 2025 - 6:00 PM | 9     |

-----------------------------------------------------------------------

API Endpoints & Sample Requests

1. GET

Returns a welcome message.

curl http://127.0.0.1:8000/


2. `GET /classes?tz=Asia/Kolkata`

Returns all upcoming classes with optional timezone conversion.


curl "http://127.0.0.1:8000/classes?tz=America/New_York"


3. `POST /book`

Books a class.

curl -X POST http://127.0.0.1:8000/book \
  -H "Content-Type: application/json" \
  -d '{
    "class_id": 1,
    "client_name": "Rajeshwari",
    "client_email": "Rajeshwari@example.com"
  }'

4. GET /bookings?email=Rajeshwari@example.com

Returns all bookings made by a client using their email address.

curl "http://127.0.0.1:8000/bookings?email=Rajeshwari@example.com"


Timezone Support

Supports conversion using any valid timezone string (e.g., `UTC`, `Asia/Kolkata`, `America/Los_Angeles`)
