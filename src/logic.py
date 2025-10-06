from datetime import datetime, date
from .db import db, Hotel, Room, Booking, hotel_schema, room_schema, booking_schema, rooms_schema, bookings_schema

class HotelBookingLogic:
    @staticmethod
    def get_all_hotels():
        """Get all hotels"""
        hotels = Hotel.query.all()
        return hotels
    
    @staticmethod
    def get_hotel_by_id(hotel_id):
        """Get hotel by ID"""
        hotel = Hotel.query.get(hotel_id)
        return hotel
    
    @staticmethod
    def get_rooms_by_hotel(hotel_id):
        """Get all rooms for a specific hotel"""
        rooms = Room.query.filter_by(hotel_id=hotel_id).all()
        return rooms
    
    @staticmethod
    def get_room_by_id(room_id):
        """Get room by ID"""
        room = Room.query.get(room_id)
        return room
    
    @staticmethod
    def get_available_rooms(hotel_id, check_in, check_out, guests=1):
        """Get available rooms for given dates and number of guests"""
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date() if isinstance(check_in, str) else check_in
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date() if isinstance(check_out, str) else check_out
        
        # Find rooms that are available and can accommodate the number of guests
        available_rooms = Room.query.filter(
            Room.hotel_id == hotel_id,
            Room.is_available == True,
            Room.max_guests >= guests
        ).all()
        
        # Filter out rooms that have conflicting bookings
        final_available_rooms = []
        for room in available_rooms:
            conflicting_booking = Booking.query.filter(
                Booking.room_id == room.id,
                Booking.status == 'confirmed',
                db.or_(
                    db.and_(Booking.check_in_date <= check_in_date, Booking.check_out_date > check_in_date),
                    db.and_(Booking.check_in_date < check_out_date, Booking.check_out_date >= check_out_date),
                    db.and_(Booking.check_in_date >= check_in_date, Booking.check_out_date <= check_out_date)
                )
            ).first()
            
            if not conflicting_booking:
                final_available_rooms.append(room)
        
        return final_available_rooms
    
    @staticmethod
    def create_booking(room_id, guest_name, guest_email, check_in, check_out):
        """Create a new booking"""
        try:
            # Convert string dates to date objects if necessary
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date() if isinstance(check_in, str) else check_in
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date() if isinstance(check_out, str) else check_out
            
            # Validate dates
            if check_in_date >= check_out_date:
                return None, "Check-out date must be after check-in date"
            
            if check_in_date < date.today():
                return None, "Check-in date cannot be in the past"
            
            # Get room and calculate total price
            room = Room.query.get(room_id)
            if not room:
                return None, "Room not found"
            
            if not room.is_available:
                return None, "Room is not available"
            
            # Check for conflicting bookings
            conflicting_booking = Booking.query.filter(
                Booking.room_id == room_id,
                Booking.status == 'confirmed',
                db.or_(
                    db.and_(Booking.check_in_date <= check_in_date, Booking.check_out_date > check_in_date),
                    db.and_(Booking.check_in_date < check_out_date, Booking.check_out_date >= check_out_date),
                    db.and_(Booking.check_in_date >= check_in_date, Booking.check_out_date <= check_out_date)
                )
            ).first()
            
            if conflicting_booking:
                return None, "Room is not available for the selected dates"
            
            # Calculate number of nights and total price
            nights = (check_out_date - check_in_date).days
            total_price = room.price_per_night * nights
            
            # Create booking
            booking = Booking(
                room_id=room_id,
                guest_name=guest_name,
                guest_email=guest_email,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                total_price=total_price,
                status='confirmed'
            )
            
            db.session.add(booking)
            db.session.commit()
            
            return booking, None
            
        except Exception as e:
            db.session.rollback()
            return None, f"Error creating booking: {str(e)}"
    
    @staticmethod
    def get_all_bookings():
        """Get all bookings"""
        bookings = Booking.query.all()
        return bookings
    
    @staticmethod
    def get_booking_by_id(booking_id):
        """Get booking by ID"""
        booking = Booking.query.get(booking_id)
        return booking
    
    @staticmethod
    def cancel_booking(booking_id):
        """Cancel a booking"""
        try:
            booking = Booking.query.get(booking_id)
            if not booking:
                return False, "Booking not found"
            
            booking.status = 'cancelled'
            db.session.commit()
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error cancelling booking: {str(e)}"
    
    @staticmethod
    def get_bookings_by_email(guest_email):
        """Get all bookings for a guest email"""
        bookings = Booking.query.filter_by(guest_email=guest_email).all()
        return bookings
    
    @staticmethod
    def calculate_booking_price(room_id, check_in, check_out):
        """Calculate price for a potential booking"""
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date() if isinstance(check_in, str) else check_in
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date() if isinstance(check_out, str) else check_out
            
            room = Room.query.get(room_id)
            if not room:
                return None, "Room not found"
            
            nights = (check_out_date - check_in_date).days
            total_price = room.price_per_night * nights
            
            return total_price, None
            
        except Exception as e:
            return None, f"Error calculating price: {str(e)}"