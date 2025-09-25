#Frontend---->API------>logic----->db------>Response
# api/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys, os

# --- Import ReservationManager ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.logic import ReservationManager

# ------------ App Setup ------------
app = FastAPI(title="Hotel Reservation API", version="1.0")

# --- Allow frontend (Streamlit/React) to call the API ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins (Frontend apps)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Create ReservationManager instance (business logic) ---
reservation_manager = ReservationManager()

# -------- Data Models --------
class ReservationCreate(BaseModel):
    """
    Schema for creating a reservation
    """
    hotel_name: str
    hotel_location: str
    room_type: str
    price: float
    guest_name: str
    check_in_date: str
    check_out_date: str


class ReservationUpdate(BaseModel):
    """
    Schema for updating reservation details
    """
    hotel_name: str | None = None
    hotel_location: str | None = None
    room_type: str | None = None
    price: float | None = None
    guest_name: str | None = None
    check_in_date: str | None = None
    check_out_date: str | None = None


# -------------- Endpoints --------------
@app.get("/")
def home():
    """Check if the API is running"""
    return {"message": "Hotel Reservation API is running!"}


@app.get("/reservations")
def get_reservations():
    """Get all reservations"""
    return reservation_manager.get_all_reservations()


@app.post("/reservations")
def create_reservation(reservation: ReservationCreate):
    """Add a new reservation"""
    result = reservation_manager.add_reservation(
        reservation.hotel_name,
        reservation.hotel_location,
        reservation.room_type,
        reservation.price,
        reservation.guest_name,
        reservation.check_in_date,
        reservation.check_out_date,
    )
    if not result.get("Success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@app.put("/reservations/{reservation_id}")
def update_reservation(reservation_id: int, reservation: ReservationUpdate):
    """Update an existing reservation"""
    result = reservation_manager.modify_reservation(
        reservation_id,
        reservation.hotel_name,
        reservation.hotel_location,
        reservation.room_type,
        reservation.price,
        reservation.guest_name,
        reservation.check_in_date,
        reservation.check_out_date,
    )
    if not result.get("Success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@app.delete("/reservations/{reservation_id}")
def delete_reservation(reservation_id: int):
    """Delete a reservation"""
    result = reservation_manager.remove_reservation(reservation_id)
    if not result.get("Success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result
