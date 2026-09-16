# PRAYAN Database

## Overview

PRAYAN uses a relational MySQL database hosted on Aiven Cloud.

The database centrally stores users, cars, drivers, bookings and reviews for the Smart Car & Driver Rental Platform.

## Database Tables

### users
Stores registered customer information.

- user_id - Primary key
- name
- email - Unique
- phone
- password_hash

### cars
Stores rental vehicle information.

- car_id - Primary key
- car_number - Unique
- car_model
- car_type
- seats
- price_per_day
- availability_status

### drivers
Stores driver information.

- driver_id - Primary key
- name
- phone
- license_number - Unique
- experience
- price_per_day
- availability_status

### bookings
Stores booking and trip information.

- booking_id - Primary key
- user_id - Foreign key
- car_id - Foreign key, optional
- driver_id - Foreign key, optional
- pickup_location
- destination
- start_date
- end_date
- service_type
- total_price
- booking_status
- created_at

### reviews
Stores feedback for completed bookings.

- review_id - Primary key
- user_id - Foreign key
- booking_id - Foreign key
- rating
- comment
- created_at

## Relationships

- users → bookings : One-to-Many
- cars → bookings : One-to-Many
- drivers → bookings : One-to-Many
- users → reviews : One-to-Many
- bookings → reviews : One-to-Many

The car_id and driver_id fields in bookings can be NULL because PRAYAN supports Car Only, Driver Only, and Car + Driver services.

## Booking Scenarios Tested

1. Car Only: Amravati → Nagpur
2. Driver Only: Amravati → Pune
3. Car + Driver: Amravati → Mumbai

## Database Files

- `schema.sql` - Creates the database tables and relationships.
- `sample_data.sql` - Inserts demonstration users, cars, drivers, bookings and reviews.
- `db.py` - Provides the Python connection to the Aiven MySQL database.
- `prayan_erd.png` - ER diagram showing the database relationships.

## Security

Database credentials are stored in environment variables using `.env`.

The `.env` file is excluded from Git using `.gitignore`.

Passwords, database credentials and other secrets must not be committed to GitHub.

## Integration

The database schema is shared with the Flask backend and booking modules so that all team members use the same table and column structure.