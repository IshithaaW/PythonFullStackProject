#db_manager.py
import os 
from supabase import create_client
from dotenv import load_dotenv

#loading environment variables from .env file
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

# Create a reservation
def create_reservation(hotel_name, hotel_location, room_type, price, guest_name, check_in_date, check_out_date):
    data = {
        "hotel_name": hotel_name,
        "hotel_location": hotel_location,
        "room_type": room_type,
        "price": price,
        "guest_name": guest_name,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date
    }
    response = supabase.table("reservations").insert(data).execute()
    return response

# Get all reservations
def get_all_reservations():
    response = supabase.table("reservations").select("*").execute()
    return response

# Update reservation
def update_reservation(reservation_id, hotel_name=None, hotel_location=None, room_type=None, price=None, guest_name=None, check_in_date=None, check_out_date=None):
    data = {}
    if hotel_name:
        data["hotel_name"] = hotel_name
    if hotel_location:
        data["hotel_location"] = hotel_location
    if room_type:
        data["room_type"] = room_type
    if price:
        data["price"] = price
    if guest_name:
        data["guest_name"] = guest_name
    if check_in_date:
        data["check_in_date"] = check_in_date
    if check_out_date:
        data["check_out_date"] = check_out_date

    response = supabase.table("reservations").update(data).eq("id", reservation_id).execute()
    return response

# Delete reservation
def delete_reservation(reservation_id):
    response = supabase.table("reservations").delete().eq("id", reservation_id).execute()
    return response
