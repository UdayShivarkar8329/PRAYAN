from database.db import get_connection
from datetime import datetime


def get_available_cars():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT car_id, car_number, car_model,
                       car_type, seats, price_per_day
                FROM cars
                WHERE availability_status = 'available'
                ORDER BY car_id
            """)

            return cursor.fetchall()

    finally:
        connection.close()


def get_available_drivers():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT driver_id, name, phone,
                       experience, price_per_day
                FROM drivers
                WHERE availability_status = 'available'
                ORDER BY driver_id
            """)

            return cursor.fetchall()

    finally:
        connection.close()


def calculate_days(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    if end < start:
        return None

    return (end - start).days + 1


def calculate_total_price(
    service_type,
    car_id,
    driver_id,
    start_date,
    end_date
):

    days = calculate_days(start_date, end_date)

    if days is None:
        return None

    connection = get_connection()

    try:
        total = 0

        with connection.cursor() as cursor:

            if service_type in ["Car Only", "Car + Driver"]:

                if not car_id:
                    return None

                cursor.execute(
                    """
                    SELECT price_per_day
                    FROM cars
                    WHERE car_id = %s
                    AND availability_status = 'available'
                    """,
                    (car_id,)
                )

                car = cursor.fetchone()

                if not car:
                    return None

                total += float(car["price_per_day"]) * days

            if service_type in ["Driver Only", "Car + Driver"]:

                if not driver_id:
                    return None

                cursor.execute(
                    """
                    SELECT price_per_day
                    FROM drivers
                    WHERE driver_id = %s
                    AND availability_status = 'available'
                    """,
                    (driver_id,)
                )

                driver = cursor.fetchone()

                if not driver:
                    return None

                total += float(driver["price_per_day"]) * days

        return total

    finally:
        connection.close()


def create_booking(
    user_id,
    car_id,
    driver_id,
    pickup_location,
    destination,
    start_date,
    end_date,
    service_type,
    total_price
):

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO bookings
                (
                    user_id,
                    car_id,
                    driver_id,
                    pickup_location,
                    destination,
                    start_date,
                    end_date,
                    service_type,
                    total_price,
                    booking_status
                )
                VALUES
                (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, 'confirmed'
                )
                """,
                (
                    user_id,
                    car_id,
                    driver_id,
                    pickup_location,
                    destination,
                    start_date,
                    end_date,
                    service_type,
                    total_price
                )
            )

            booking_id = cursor.lastrowid

            connection.commit()

            return booking_id

    except Exception:

        connection.rollback()
        raise

    finally:
        connection.close()