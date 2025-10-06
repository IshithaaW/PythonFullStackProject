import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import json

# API base URL
API_BASE_URL = "http://localhost:5001/api"

def init_session_state():
    """Initialize session state variables"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    if 'selected_hotel' not in st.session_state:
        st.session_state.selected_hotel = None
    if 'selected_room' not in st.session_state:
        st.session_state.selected_room = None

def call_api(endpoint, method='GET', data=None):
    """Helper function to call API endpoints"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, json=data)
        elif method == 'DELETE':
            response = requests.delete(url)
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, response.json().get('error', 'Unknown error occurred')
    
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to the API server. Please make sure the backend is running."
    except Exception as e:
        return None, str(e)

def home_page():
    """Home page with overview"""
    st.title("🏨 Hotel Booking System")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Hotels", "3", "Luxury Locations")
    
    with col2:
        st.metric("Rooms", "9", "Various Types")
    
    with col3:
        st.metric("Bookings", "All your needs", "24/7 Service")
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Browse Hotels", use_container_width=True):
            st.session_state.current_page = "Browse Hotels"
            st.rerun()
    
    with col2:
        if st.button("Check Availability", use_container_width=True):
            st.session_state.current_page = "Check Availability"
            st.rerun()
    
    with col3:
        if st.button("My Bookings", use_container_width=True):
            st.session_state.current_page = "My Bookings"
            st.rerun()

def browse_hotels_page():
    """Page to browse all hotels"""
    st.title("🏨 Browse Hotels")
    st.markdown("---")
    
    # Fetch hotels from API
    hotels, error = call_api('/hotels')
    
    if error:
        st.error(f"Error fetching hotels: {error}")
        return
    
    if not hotels:
        st.info("No hotels found.")
        return
    
    # Display hotels
    for hotel in hotels:
        with st.container():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.image("https://via.placeholder.com/200x150?text=Hotel+Image", width=200)
            
            with col2:
                st.subheader(hotel['name'])
                st.write(f"📍 {hotel['location']}")
                st.write(hotel.get('description', 'No description available.'))
                
                if st.button(f"View Rooms", key=f"view_rooms_{hotel['id']}"):
                    st.session_state.current_page = "Hotel Details"
                    st.session_state.selected_hotel = hotel
                    st.rerun()
            
            st.markdown("---")

def hotel_details_page():
    """Page showing hotel details and rooms"""
    hotel = st.session_state.selected_hotel
    
    st.title(f"🏨 {hotel['name']}")
    st.write(f"📍 {hotel['location']}")
    st.markdown("---")
    
    # Fetch rooms for this hotel
    rooms, error = call_api(f"/hotels/{hotel['id']}/rooms")
    
    if error:
        st.error(f"Error fetching rooms: {error}")
        return
    
    if not rooms:
        st.info("No rooms available for this hotel.")
        return
    
    # Display rooms
    st.subheader("Available Rooms")
    
    for room in rooms:
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                room_type_emoji = "🛌" if "single" in room['room_type'].lower() else "🛏️" if "double" in room['room_type'].lower() else "🏨"
                st.write(f"### {room_type_emoji} {room['room_type']}")
                st.write(f"**Room:** {room['room_number']}")
                st.write(f"**Max Guests:** {room['max_guests']}")
            
            with col2:
                st.write(f"**Description:** {room.get('description', 'Comfortable room with all amenities.')}")
                status_color = "🟢" if room['is_available'] else "🔴"
                st.write(f"**Status:** {status_color} {'Available' if room['is_available'] else 'Not Available'}")
            
            with col3:
                st.write(f"### ${room['price_per_night']}/night")
                if room['is_available']:
                    if st.button("Book Now", key=f"book_{room['id']}"):
                        st.session_state.current_page = "Book Room"
                        st.session_state.selected_room = room
                        st.rerun()
                else:
                    st.button("Not Available", disabled=True)
            
            st.markdown("---")

def check_availability_page():
    """Page to check room availability"""
    st.title("🔍 Check Room Availability")
    st.markdown("---")
    
    # Fetch hotels for selection
    hotels, error = call_api('/hotels')
    
    if error:
        st.error(f"Error fetching hotels: {error}")
        return
    
    if not hotels:
        st.info("No hotels found.")
        return
    
    # Availability form
    with st.form("availability_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            hotel_options = {hotel['name']: hotel['id'] for hotel in hotels}
            selected_hotel_name = st.selectbox("Select Hotel", list(hotel_options.keys()))
            hotel_id = hotel_options[selected_hotel_name]
        
        with col2:
            check_in = st.date_input("Check-in Date", min_value=date.today())
        
        with col3:
            check_out = st.date_input("Check-out Date", min_value=date.today() + timedelta(days=1))
        
        guests = st.number_input("Number of Guests", min_value=1, max_value=10, value=2)
        
        if st.form_submit_button("Check Availability", use_container_width=True):
            if check_in >= check_out:
                st.error("Check-out date must be after check-in date.")
            else:
                # Call API to get available rooms
                endpoint = f"/hotels/{hotel_id}/available-rooms?check_in={check_in}&check_out={check_out}&guests={guests}"
                available_rooms, error = call_api(endpoint)
                
                if error:
                    st.error(f"Error checking availability: {error}")
                else:
                    if available_rooms:
                        st.success(f"Found {len(available_rooms)} available rooms!")
                        
                        # Display available rooms
                        for room in available_rooms:
                            with st.container():
                                col1, col2, col3 = st.columns([2, 2, 1])
                                
                                with col1:
                                    st.write(f"**{room['room_type']}** - Room {room['room_number']}")
                                    st.write(f"Max Guests: {room['max_guests']}")
                                
                                with col2:
                                    nights = (check_out - check_in).days
                                    total_price = room['price_per_night'] * nights
                                    st.write(f"**${room['price_per_night']}/night**")
                                    st.write(f"Total: ${total_price:.2f} for {nights} nights")
                                
                                with col3:
                                    if st.button("Book", key=f"avail_book_{room['id']}"):
                                        st.session_state.current_page = "Book Room"
                                        st.session_state.selected_room = room
                                        st.session_state.check_in = check_in
                                        st.session_state.check_out = check_out
                                        st.rerun()
                                
                                st.markdown("---")
                    else:
                        st.warning("No rooms available for the selected dates and criteria.")

def book_room_page():
    """Page to book a room"""
    room = st.session_state.selected_room
    
    st.title("📝 Book a Room")
    st.markdown("---")
    
    # Room details
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Room Details")
        st.write(f"**Hotel:** {room['hotel']['name']}")
        st.write(f"**Room Type:** {room['room_type']}")
        st.write(f"**Room Number:** {room['room_number']}")
        st.write(f"**Max Guests:** {room['max_guests']}")
        st.write(f"**Price per night:** ${room['price_per_night']}")
    
    with col2:
        st.subheader("Booking Details")
        
        # Date selection
        check_in = st.session_state.get('check_in', date.today())
        check_out = st.session_state.get('check_out', date.today() + timedelta(days=1))
        
        new_check_in = st.date_input("Check-in Date", value=check_in, min_value=date.today())
        new_check_out = st.date_input("Check-out Date", value=check_out, min_value=new_check_in + timedelta(days=1))
        
        if new_check_in != check_in or new_check_out != check_out:
            # Recalculate price if dates change
            check_in = new_check_in
            check_out = new_check_out
            st.session_state.check_in = check_in
            st.session_state.check_out = check_out
        
        nights = (check_out - check_in).days
        total_price = room['price_per_night'] * nights
        
        st.write(f"**Nights:** {nights}")
        st.write(f"**Total Price:** ${total_price:.2f}")
    
    st.markdown("---")
    
    # Guest information form
    st.subheader("Guest Information")
    
    with st.form("booking_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            guest_name = st.text_input("Full Name", placeholder="Enter your full name")
        
        with col2:
            guest_email = st.text_input("Email Address", placeholder="Enter your email")
        
        if st.form_submit_button("Confirm Booking", use_container_width=True):
            if not guest_name or not guest_email:
                st.error("Please fill in all required fields.")
            elif check_in >= check_out:
                st.error("Check-out date must be after check-in date.")
            else:
                # Create booking
                booking_data = {
                    'room_id': room['id'],
                    'guest_name': guest_name,
                    'guest_email': guest_email,
                    'check_in': check_in.isoformat(),
                    'check_out': check_out.isoformat()
                }
                
                booking, error = call_api('/bookings', method='POST', data=booking_data)
                
                if error:
                    st.error("🎉 Booking confirmed successfully!")
                else:
                    st.success("🎉 Booking confirmed successfully!")
                    st.balloons()
                    
                    # Show booking details
                    st.subheader("Booking Confirmation")
                    st.write(f"**Booking ID:** #{booking['id']}")
                    st.write(f"**Guest:** {booking['guest_name']}")
                    st.write(f"**Dates:** {booking['check_in_date']} to {booking['check_out_date']}")
                    st.write(f"**Total Paid:** ${booking['total_price']:.2f}")
                    
                    if st.button("Back to Home"):
                        st.session_state.current_page = "Home"
                        st.rerun()

def my_bookings_page():
    """Page to view user's bookings"""
    st.title("📋 My Bookings")
    st.markdown("---")
    
    # Email input to search bookings
    guest_email = st.text_input("Enter your email to view bookings", placeholder="your.email@example.com")
    
    if guest_email:
        bookings, error = call_api(f"/bookings/guest/{guest_email}")
        
        if error:
            st.error(f"Error fetching bookings: {error}")
        else:
            if not bookings:
                st.info("No bookings found for this email address.")
            else:
                # Display bookings in a table
                booking_data = []
                for booking in bookings:
                    booking_data.append({
                        'Booking ID': booking['id'],
                        'Hotel': booking['room']['hotel']['name'],
                        'Room': f"{booking['room']['room_type']} ({booking['room']['room_number']})",
                        'Check-in': booking['check_in_date'],
                        'Check-out': booking['check_out_date'],
                        'Total Price': f"${booking['total_price']:.2f}",
                        'Status': booking['status']
                    })
                
                df = pd.DataFrame(booking_data)
                st.dataframe(df, use_container_width=True)
                
                # Booking actions
                st.subheader("Booking Actions")
                booking_id = st.number_input("Enter Booking ID to cancel", min_value=1, step=1)
                
                if st.button("Cancel Booking", type="secondary"):
                    if booking_id:
                        success, error = call_api(f"/bookings/{booking_id}", method='DELETE')
                        
                        if error:
                            st.error(f"Error cancelling booking: {error}")
                        else:
                            st.success("Booking cancelled successfully!")
                            st.rerun()
                    else:
                        st.error("Please enter a valid Booking ID")

def main():
    """Main application"""
    # Page configuration
    st.set_page_config(
        page_title="Hotel Booking System",
        page_icon="🏨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🏨 Navigation")
        st.markdown("---")
        
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = "Home"
            st.rerun()
        
        if st.button("🏨 Browse Hotels", use_container_width=True):
            st.session_state.current_page = "Browse Hotels"
            st.rerun()
        
        if st.button("🔍 Check Availability", use_container_width=True):
            st.session_state.current_page = "Check Availability"
            st.rerun()
        
        if st.button("📋 My Bookings", use_container_width=True):
            st.session_state.current_page = "My Bookings"
            st.rerun()
        
        st.markdown("---")
        st.write("### About")
        st.write("Hotel Booking System v1.0")
        st.write("Built with Streamlit & Flask")
    
    # Display current page
    if st.session_state.current_page == "Home":
        home_page()
    elif st.session_state.current_page == "Browse Hotels":
        browse_hotels_page()
    elif st.session_state.current_page == "Hotel Details":
        hotel_details_page()
    elif st.session_state.current_page == "Check Availability":
        check_availability_page()
    elif st.session_state.current_page == "Book Room":
        book_room_page()
    elif st.session_state.current_page == "My Bookings":
        my_bookings_page()

if __name__ == "__main__":
    main()