create table users (
    user_id int primary key auto_increment,
    name varchar(100) not null,
    email varchar(150) not null unique,
    phone varchar(20),
    password_hash varchar(255) not null,
    role varchar(20) not null default 'user'
);

create table cars (
    car_id int primary key auto_increment,
    car_number varchar(30) not null unique,
    car_model varchar(100) not null,
    car_type varchar(50),
    seats int,
    price_per_day decimal(10,2),
    availability_status varchar(30) default 'available'
);

create table drivers (
    driver_id int primary key auto_increment,
    name varchar(100) not null,
    phone varchar(20),
    license_number varchar(50) not null unique,
    experience int,
    price_per_day decimal(10,2),
    availability_status varchar(30) default 'available'
);

create table bookings (
    booking_id int primary key auto_increment,
    user_id int not null,
    car_id int null,
    driver_id int null,
    pickup_location varchar(150) not null,
    destination varchar(150) not null,
    start_date date not null,
    end_date date not null,
    service_type varchar(30) not null,
    total_price decimal(10,2) not null,
    booking_status varchar(30) default 'confirmed',
    created_at timestamp default current_timestamp,
    foreign key (user_id) references users(user_id),
    foreign key (car_id) references cars(car_id),
    foreign key (driver_id) references drivers(driver_id)
);

create table reviews (
    review_id int primary key auto_increment,
    user_id int not null,
    booking_id int not null,
    rating int,
    comment varchar(500),
    created_at timestamp default current_timestamp,
    foreign key (user_id) references users(user_id),
    foreign key (booking_id) references bookings(booking_id)
);