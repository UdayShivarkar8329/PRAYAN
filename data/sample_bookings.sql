-- PRAYAN Member 11: Sample Booking Test Data
-- Fictional/demo data for testing only
--
-- Demo pricing assumption:
-- total_price = applicable daily rate × number of rental days
-- This is test data only until the project's booking/pricing logic is implemented.

-- 1. Car Only
INSERT INTO bookings
(user_id, car_id, driver_id, pickup_location, destination,
 start_date, end_date, service_type, total_price, booking_status)
SELECT
    u.user_id,
    c.car_id,
    NULL,
    'Amravati',
    'Akola',
    '2026-10-15',
    '2026-10-16',
    'Car Only',
    c.price_per_day,
    'confirmed'
FROM users u
JOIN cars c ON c.car_number = 'MH27EF2468'
WHERE u.email = 'aarav@example.com';


-- 2. Driver Only
INSERT INTO bookings
(user_id, car_id, driver_id, pickup_location, destination,
 start_date, end_date, service_type, total_price, booking_status)
SELECT
    u.user_id,
    NULL,
    d.driver_id,
    'Amravati',
    'Wardha',
    '2026-10-18',
    '2026-10-19',
    'Driver Only',
    d.price_per_day,
    'confirmed'
FROM users u
JOIN drivers d ON d.license_number = 'LIC2001'
WHERE u.email = 'sneha@example.com';


-- 3. Car + Driver
INSERT INTO bookings
(user_id, car_id, driver_id, pickup_location, destination,
 start_date, end_date, service_type, total_price, booking_status)
SELECT
    u.user_id,
    c.car_id,
    d.driver_id,
    'Amravati',
    'Nagpur',
    '2026-10-20',
    '2026-10-22',
    'Car + Driver',
    (c.price_per_day + d.price_per_day) * 2,
    'confirmed'
FROM users u
JOIN cars c ON c.car_number = 'MH27GH1357'
JOIN drivers d ON d.license_number = 'LIC2002'
WHERE u.email = 'aarav@example.com';


-- 4. Car Only - Cancelled booking
INSERT INTO bookings
(user_id, car_id, driver_id, pickup_location, destination,
 start_date, end_date, service_type, total_price, booking_status)
SELECT
    u.user_id,
    c.car_id,
    NULL,
    'Amravati',
    'Nashik',
    '2026-10-25',
    '2026-10-26',
    'Car Only',
    c.price_per_day,
    'cancelled'
FROM users u
JOIN cars c ON c.car_number = 'MH27JK8642'
WHERE u.email = 'sneha@example.com';


-- 5. Car + Driver - Pending booking
INSERT INTO bookings
(user_id, car_id, driver_id, pickup_location, destination,
 start_date, end_date, service_type, total_price, booking_status)
SELECT
    u.user_id,
    c.car_id,
    d.driver_id,
    'Amravati',
    'Pune',
    '2026-10-28',
    '2026-10-30',
    'Car + Driver',
    (c.price_per_day + d.price_per_day) * 2,
    'pending'
FROM users u
JOIN cars c ON c.car_number = 'MH27NP4826'
JOIN drivers d ON d.license_number = 'LIC2003'
WHERE u.email = 'aarav@example.com';