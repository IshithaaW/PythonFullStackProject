# Hotel/Room Reservation System API

## Project Description

The Hotel/Room Reservation System API is a RESTful API built with Python and Flask that allows users to manage hotel room bookings efficiently. It provides endpoints to view hotels, explore available rooms, and create reservations. The API is designed to be simple yet extensible, making it easy to add advanced features like authentication, cancellation, and real-time availability checking.

This system is ideal for developers who want a backend service for hotel booking applications or for learning how to build and structure RESTful APIs using Flask and SQLAlchemy.

## Features

Hotel Management:
View a list of all hotels
Fetch hotel details including location

Room Management:
List all rooms in a specific hotel
Fetch room details such as room type, price, and availability

Booking Management:
Create new bookings for a room
View all existing bookings
Store booking details including guest name, check-in, and check-out dates

Database Integration:
Use SQLite for storing hotels, rooms, and bookings
Easily switchable to PostgreSQL or MySQL for production

Extensible API:
Ready for features like authentication, booking cancellation, and availability checks
Can be integrated with front-end applications or mobile apps

Validation & Serialization:
Uses Marshmallow to validate incoming requests and serialize responses

## project structure

Hotel Booking/
|
|---src/                 #core application logic
|     |---logic.py       #Business logic and task
operations
|     |__db.py           #database operations
|
|---api/                 #Backend api
|     |__main.py         #FastAPI endpoints
|
|---frontend/            #frontend application
|     |__app.py          #streamlit application
|
|___requirements.txt     #Python Dependencies
|
|___README.md            #Project documentation
|
|___.env                 #Python Variables 
