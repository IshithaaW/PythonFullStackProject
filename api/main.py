import sys
import os
from flask import Flask, request, jsonify
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.db import init_db, hotel_schema, room_schema, booking_schema, hotels_schema, rooms_schema, bookings_schema
from src.logic import HotelBookingLogic

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///hotel_booking.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Initialize database
init_db(app)

@app.route('/')
def home():
    return jsonify({
        "message": "Hotel/Room Reservation System API",
        "version": "1.0.0",
        "endpoints": {
            "hotels": "/api/hotels",
            "hotel_detail": "/api/hotels/<int:hotel_id>",
            "hotel_rooms": "/api/hotels/<int:hotel_id>/rooms",
            "available_rooms": "/api/hotels/<int:hotel_id>/available-rooms",
            "room_detail": "/api/rooms/<int:room_id>",
            "bookings": "/api/bookings",
            "booking_detail": "/api/bookings/<int:booking_id>",
            "guest_bookings": "/api/bookings/guest/<string:guest_email>"
        }
    })

# Hotel endpoints
@app.route('/api/hotels', methods=['GET'])
def get_hotels():
    """Get all hotels"""
    try:
        hotels = HotelBookingLogic.get_all_hotels()
        return jsonify(hotels_schema.dump(hotels))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/hotels/<int:hotel_id>', methods=['GET'])
def get_hotel(hotel_id):
    """Get hotel by ID"""
    try:
        hotel = HotelBookingLogic.get_hotel_by_id(hotel_id)
        if not hotel:
            return jsonify({"error": "Hotel not found"}), 404
        return jsonify(hotel_schema.dump(hotel))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Room endpoints
@app.route('/api/hotels/<int:hotel_id>/rooms', methods=['GET'])
def get_hotel_rooms(hotel_id):
    """Get all rooms for a specific hotel"""
    try:
        rooms = HotelBookingLogic.get_rooms_by_hotel(hotel_id)
        return jsonify(rooms_schema.dump(rooms))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/rooms/<int:room_id>', methods=['GET'])
def get_room(room_id):
    """Get room by ID"""
    try:
        room = HotelBookingLogic.get_room_by_id(room_id)
        if not room:
            return jsonify({"error": "Room not found"}), 404
        return jsonify(room_schema.dump(room))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/hotels/<int:hotel_id>/available-rooms', methods=['GET'])
def get_available_rooms(hotel_id):
    """Get available rooms for given dates"""
    try:
        check_in = request.args.get('check_in')
        check_out = request.args.get('check_out')
        guests = request.args.get('guests', 1, type=int)
        
        if not check_in or not check_out:
            return jsonify({"error": "check_in and check_out parameters are required"}), 400
        
        # Validate date format
        try:
            datetime.strptime(check_in, '%Y-%m-%d')
            datetime.strptime(check_out, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        available_rooms = HotelBookingLogic.get_available_rooms(hotel_id, check_in, check_out, guests)
        return jsonify(rooms_schema.dump(available_rooms))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Booking endpoints
@app.route('/api/bookings', methods=['GET', 'POST'])
def handle_bookings():
    """Get all bookings or create a new booking"""
    if request.method == 'GET':
        try:
            bookings = HotelBookingLogic.get_all_bookings()
            return jsonify(bookings_schema.dump(bookings))
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            required_fields = ['room_id', 'guest_name', 'guest_email', 'check_in', 'check_out']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400
            
            booking, error = HotelBookingLogic.create_booking(
                data['room_id'],
                data['guest_name'],
                data['guest_email'],
                data['check_in'],
                data['check_out']
            )
            
            if error:
                return jsonify({"error": error}), 400
            
            return jsonify(booking_schema.dump(booking)), 201
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/bookings/<int:booking_id>', methods=['GET', 'DELETE'])
def handle_booking(booking_id):
    """Get or cancel a specific booking"""
    if request.method == 'GET':
        try:
            booking = HotelBookingLogic.get_booking_by_id(booking_id)
            if not booking:
                return jsonify({"error": "Booking not found"}), 404
            return jsonify(booking_schema.dump(booking))
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            success, error = HotelBookingLogic.cancel_booking(booking_id)
            if error:
                return jsonify({"error": error}), 400
            return jsonify({"message": "Booking cancelled successfully"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/bookings/guest/<string:guest_email>', methods=['GET'])
def get_guest_bookings(guest_email):
    """Get all bookings for a guest email"""
    try:
        bookings = HotelBookingLogic.get_bookings_by_email(guest_email)
        return jsonify(bookings_schema.dump(bookings))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/calculate-price', methods=['POST'])
def calculate_price():
    """Calculate price for a potential booking"""
    try:
        data = request.get_json()
        
        required_fields = ['room_id', 'check_in', 'check_out']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        total_price, error = HotelBookingLogic.calculate_booking_price(
            data['room_id'],
            data['check_in'],
            data['check_out']
        )
        
        if error:
            return jsonify({"error": error}), 400
        
        return jsonify({"total_price": total_price})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('DEBUG', False), host='0.0.0.0', port=5001)