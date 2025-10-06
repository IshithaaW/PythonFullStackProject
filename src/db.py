from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
ma = Marshmallow()

class Hotel(db.Model):
    __tablename__ = 'hotels'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    rooms = db.relationship('Room', backref='hotel', lazy=True, cascade='all, delete-orphan')

class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=False)
    room_number = db.Column(db.String(10), nullable=False)
    room_type = db.Column(db.String(50), nullable=False)  # single, double, suite, etc.
    price_per_night = db.Column(db.Float, nullable=False)
    max_guests = db.Column(db.Integer, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    bookings = db.relationship('Booking', backref='room', lazy=True, cascade='all, delete-orphan')

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    guest_name = db.Column(db.String(100), nullable=False)
    guest_email = db.Column(db.String(100), nullable=False)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='confirmed')  # confirmed, cancelled, completed
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# Marshmallow Schemas for serialization
class HotelSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Hotel
        include_relationships = True
        load_instance = True

class RoomSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Room
        include_fk = True
        load_instance = True
    
    hotel = ma.Nested(HotelSchema)

class BookingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Booking
        include_fk = True
        load_instance = True
    
    room = ma.Nested(RoomSchema)

# Initialize schemas
hotel_schema = HotelSchema()
hotels_schema = HotelSchema(many=True)
room_schema = RoomSchema()
rooms_schema = RoomSchema(many=True)
booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)

def init_db(app):
    """Initialize database with sample data"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # Create sample data if no hotels exist
        if Hotel.query.count() == 0:
            # Create sample hotels
            hotel1 = Hotel(
                name="Grand Plaza Hotel",
                location="New York, NY",
                description="Luxury hotel in the heart of Manhattan"
            )
            hotel2 = Hotel(
                name="Ocean View Resort",
                location="Miami, FL",
                description="Beachfront resort with stunning ocean views"
            )
            hotel3 = Hotel(
                name="Mountain Retreat",
                location="Denver, CO",
                description="Cozy hotel nestled in the Rocky Mountains"
            )
            
            db.session.add_all([hotel1, hotel2, hotel3])
            db.session.commit()
            
            # Create sample rooms for each hotel
            rooms_data = [
                # Hotel 1 rooms
                {"hotel_id": 1, "room_number": "101", "room_type": "Single", "price_per_night": 99.99, "max_guests": 1},
                {"hotel_id": 1, "room_number": "102", "room_type": "Double", "price_per_night": 149.99, "max_guests": 2},
                {"hotel_id": 1, "room_number": "201", "room_type": "Suite", "price_per_night": 299.99, "max_guests": 4},
                
                # Hotel 2 rooms
                {"hotel_id": 2, "room_number": "101", "room_type": "Single", "price_per_night": 129.99, "max_guests": 1},
                {"hotel_id": 2, "room_number": "102", "room_type": "Double", "price_per_night": 199.99, "max_guests": 2},
                {"hotel_id": 2, "room_number": "201", "room_type": "Ocean View Suite", "price_per_night": 399.99, "max_guests": 4},
                
                # Hotel 3 rooms
                {"hotel_id": 3, "room_number": "101", "room_type": "Single", "price_per_night": 79.99, "max_guests": 1},
                {"hotel_id": 3, "room_number": "102", "room_type": "Double", "price_per_night": 119.99, "max_guests": 2},
                {"hotel_id": 3, "room_number": "201", "room_type": "Mountain View Suite", "price_per_night": 199.99, "max_guests": 4},
            ]
            
            for room_data in rooms_data:
                room = Room(**room_data)
                db.session.add(room)
            
            db.session.commit()