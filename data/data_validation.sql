-- PRAYAN Member 11: Data Validation Queries
-- These queries are for testing and checking sample data.
-- They do not modify or delete any data.


-- 1. Check all cars
SELECT *
FROM cars;


-- 2. Check all drivers
SELECT *
FROM drivers;


-- 3. Check all bookings
SELECT *
FROM bookings;


-- 4. Check cars with invalid seat values
SELECT *
FROM cars
WHERE seats IS NULL OR seats <= 0;


-- 5. Check cars with invalid prices
SELECT *
FROM cars
WHERE price_per_day IS NULL OR price_per_day <= 0;


-- 6. Check drivers with invalid experience
SELECT *
FROM drivers
WHERE experience IS NULL OR experience < 0;


-- 7. Check drivers with invalid prices
SELECT *
FROM drivers
WHERE price_per_day IS NULL OR price_per_day <= 0;


-- 8. Check invalid car availability status
SELECT *
FROM cars
WHERE availability_status NOT IN ('available', 'unavailable');


-- 9. Check invalid driver availability status
SELECT *
FROM drivers
WHERE availability_status NOT IN ('available', 'unavailable');


-- 10. Check invalid booking dates
SELECT *
FROM bookings
WHERE end_date < start_date;


-- 11. Check invalid booking service types
SELECT *
FROM bookings
WHERE service_type NOT IN ('Car Only', 'Driver Only', 'Car + Driver');


-- 12. Check Car Only bookings
-- Car should be present and driver should be NULL.
SELECT *
FROM bookings
WHERE service_type = 'Car Only'
  AND (car_id IS NULL OR driver_id IS NOT NULL);


-- 13. Check Driver Only bookings
-- Driver should be present and car should be NULL.
SELECT *
FROM bookings
WHERE service_type = 'Driver Only'
  AND (driver_id IS NULL OR car_id IS NOT NULL);


-- 14. Check Car + Driver bookings
-- Both car and driver should be present.
SELECT *
FROM bookings
WHERE service_type = 'Car + Driver'
  AND (car_id IS NULL OR driver_id IS NULL);


-- 15. Check bookings with invalid user references
SELECT b.*
FROM bookings b
LEFT JOIN users u ON b.user_id = u.user_id
WHERE u.user_id IS NULL;


-- 16. Check bookings with invalid car references
SELECT b.*
FROM bookings b
LEFT JOIN cars c ON b.car_id = c.car_id
WHERE b.car_id IS NOT NULL
  AND c.car_id IS NULL;


-- 17. Check bookings with invalid driver references
SELECT b.*
FROM bookings b
LEFT JOIN drivers d ON b.driver_id = d.driver_id
WHERE b.driver_id IS NOT NULL
  AND d.driver_id IS NULL;


-- 18. Display available cars
SELECT car_id, car_number, car_model, car_type, seats, price_per_day
FROM cars
WHERE availability_status = 'available';


-- 19. Display available drivers
SELECT driver_id, name, experience, price_per_day
FROM drivers
WHERE availability_status = 'available';


-- 20. Display booking details with car and driver information
SELECT
    b.booking_id,
    u.name AS customer_name,
    c.car_model,
    d.name AS driver_name,
    b.pickup_location,
    b.destination,
    b.start_date,
    b.end_date,
    b.service_type,
    b.total_price,
    b.booking_status
FROM bookings b
JOIN users u ON b.user_id = u.user_id
LEFT JOIN cars c ON b.car_id = c.car_id
LEFT JOIN drivers d ON b.driver_id = d.driver_id;
-- Check bookings with invalid driver references
SELECT b.*
FROM bookings b
LEFT JOIN drivers d ON b.driver_id = d.driver_id
WHERE b.driver_id IS NOT NULL
  AND d.driver_id IS NULL;


-- =========================================================
-- PRAYAN Member 11 - Validation Results
-- Date: 2026-09-17
-- =========================================================

-- Record counts
SELECT COUNT(*) AS user_count FROM users;
SELECT COUNT(*) AS car_count FROM cars;
SELECT COUNT(*) AS driver_count FROM drivers;
SELECT COUNT(*) AS booking_count FROM bookings;

-- Service type distribution
SELECT service_type, COUNT(*) AS booking_count
FROM bookings
GROUP BY service_type;

...