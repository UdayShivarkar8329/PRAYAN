insert into users (name, email, phone, password_hash)
values
('aarav patil', 'aarav@example.com', '9000000011', 'demo_hash_1'),
('sneha deshmukh', 'sneha@example.com', '9000000012', 'demo_hash_2');

insert into cars
(car_number, car_model, car_type, seats, price_per_day, availability_status)
values
('MH27AB1234', 'Maruti Ertiga', 'SUV', 7, 2200.00, 'available'),
('MH27CD5678', 'Hyundai i20', 'Hatchback', 5, 1800.00, 'available');

insert into drivers
(name, phone, license_number, experience, price_per_day, availability_status)
values
('driver one', '9000000001', 'LIC1001', 5, 1200.00, 'available'),
('driver two', '9000000002', 'LIC1002', 8, 1500.00, 'available');

insert into bookings
(user_id, car_id, driver_id, pickup_location, destination,
start_date, end_date, service_type, total_price, booking_status)
values
(1, 1, null, 'Amravati', 'Nagpur',
'2026-10-01', '2026-10-02', 'Car Only', 2200.00, 'confirmed'),

(2, null, 1, 'Amravati', 'Pune',
'2026-10-05', '2026-10-06', 'Driver Only', 1200.00, 'confirmed'),

(1, 2, 2, 'Amravati', 'Mumbai',
'2026-10-10', '2026-10-12', 'Car + Driver', 5400.00, 'confirmed');

insert into reviews
(user_id, booking_id, rating, comment)
values
(1, 1, 5, 'good service'),
(2, 2, 4, 'good driver');