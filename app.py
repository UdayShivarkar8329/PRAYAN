import os

from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    session,
    flash
)

from booking.booking import (
    get_available_cars,
    get_available_drivers,
    calculate_total_price,
    create_booking
)

from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from database.db import get_connection
from maps.maps import get_route

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "temporary-development-secret"
)

# -------------------------
# HOME
# -------------------------

@app.route("/")
def home():
    return render_template("home.html")


# -------------------------
# REGISTER
# -------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")

        # Basic validation
        if not name or not email or not password:
            flash("Name, email and password are required.")
            return render_template("register.html")

        if "@" not in email or "." not in email:
            flash("Please enter a valid email address.")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.")
            return render_template("register.html")

        connection = None

        try:

            connection = get_connection()

            with connection.cursor() as cursor:

                # Check whether email already exists
                cursor.execute(
                    "SELECT user_id FROM users WHERE email = %s",
                    (email,)
                )

                existing_user = cursor.fetchone()

                if existing_user:
                    flash("An account with this email already exists.")
                    return render_template("register.html")

                # Hash password
                password_hash = generate_password_hash(password)

                cursor.execute(
                    """
                    INSERT INTO users
                    (name, email, phone, password_hash)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        name,
                        email,
                        phone,
                        password_hash
                    )
                )

                connection.commit()

            flash("Registration successful. Please login.")
            return redirect(url_for("login"))

        except Exception as e:

            if connection:
                connection.rollback()

            print("Registration error:", e)

            flash("Something went wrong during registration.")

            return render_template("register.html")

        finally:

            if connection:
                connection.close()

    return render_template("register.html")


# -------------------------
# LOGIN
# -------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.")
            return render_template("login.html")

        connection = None

        try:

            connection = get_connection()

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT user_id, name, email, password_hash
                    FROM users
                    WHERE email = %s
                    """,
                    (email,)
                )

                user = cursor.fetchone()

            if not user:

                flash("Invalid email or password.")

                return render_template("login.html")

            # Check hashed password
            if not check_password_hash(
                user["password_hash"],
                password
            ):

                flash("Invalid email or password.")

                return render_template("login.html")

            # Store user information in session
            session["user_id"] = user["user_id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]

            return redirect(url_for("dashboard"))

        except Exception as e:

            print("Login error:", e)

            flash("Something went wrong during login.")

            return render_template("login.html")

        finally:

            if connection:
                connection.close()

    return render_template("login.html")


# -------------------------
# DASHBOARD
# -------------------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        flash("Please login first.")

        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        user_name=session.get("user_name")
    )


# -------------------------
# LOGOUT
# -------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.")

    return redirect(url_for("login"))


# -------------------------
# ROUTE / MAP
# -------------------------

@app.route("/route")
def route():

    pickup_location = request.args.get("pickup_location")
    destination = request.args.get("destination")

    if not pickup_location:
        return "Please enter a pickup location."

    if not destination:
        return "Please enter a destination."

    result = get_route(
        pickup_location,
        destination
    )

    return result


# -------------------------
# CARS
# -------------------------

@app.route("/cars")
def cars():

    if "user_id" not in session:

        flash("Please login first.")

        return redirect(url_for("login"))

    connection = None

    try:

        connection = get_connection()

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    car_id,
                    car_number,
                    car_model,
                    car_type,
                    seats,
                    price_per_day,
                    availability_status
                FROM cars
                ORDER BY car_id
                """
            )

            cars_list = cursor.fetchall()

        return render_template(
            "cars.html",
            cars=cars_list
        )

    except Exception as e:

        print("Cars error:", e)

        flash("Unable to load cars.")

        return render_template(
            "cars.html",
            cars=[]
        )

    finally:

        if connection:
            connection.close()


# -------------------------
# DRIVERS
# -------------------------

@app.route("/drivers")
def drivers():

    if "user_id" not in session:

        flash("Please login first.")

        return redirect(url_for("login"))

    connection = None

    try:

        connection = get_connection()

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    driver_id,
                    name,
                    phone,
                    license_number,
                    experience,
                    price_per_day,
                    availability_status
                FROM drivers
                ORDER BY driver_id
                """
            )

            drivers_list = cursor.fetchall()

        return render_template(
            "drivers.html",
            drivers=drivers_list
        )

    except Exception as e:

        print("Drivers error:", e)

        flash("Unable to load drivers.")

        return render_template(
            "drivers.html",
            drivers=[]
        )

    finally:

        if connection:
            connection.close()


# -------------------------
# BOOKING PAGE
# -------------------------

@app.route("/booking", methods=["GET", "POST"])
def booking():

    # Get available cars and drivers
    cars = get_available_cars()
    drivers = get_available_drivers()

    # -------------------------
    # GET REQUEST
    # -------------------------

    if request.method == "GET":

        pickup_location = request.args.get(
            "pickup_location",
            ""
        )

        destination = request.args.get(
            "destination",
            ""
        )

        selected_car_id = request.args.get(
            "car_id",
            ""
        )

        return render_template(
            "booking.html",
            cars=cars,
            drivers=drivers,
            pickup_location=pickup_location,
            destination=destination,
            selected_car_id=selected_car_id
        )

    # -------------------------
    # LOGIN REQUIRED
    # -------------------------

    if "user_id" not in session:

        flash("Please login to confirm your booking.")

        return redirect(url_for("login"))

    # -------------------------
    # GET FORM DATA
    # -------------------------

    pickup_location = request.form.get(
        "pickup_location",
        ""
    ).strip()

    destination = request.form.get(
        "destination",
        ""
    ).strip()

    service_type = request.form.get(
        "service_type"
    )

    car_id = request.form.get(
        "car_id"
    ) or None

    driver_id = request.form.get(
        "driver_id"
    ) or None

    start_date = request.form.get(
        "start_date"
    )

    end_date = request.form.get(
        "end_date"
    )

    # -------------------------
    # VALIDATION
    # -------------------------

    if not pickup_location:

        flash("Please enter a pickup location.")

        return redirect(url_for("booking"))

    if not destination:

        flash("Please enter a destination.")

        return redirect(url_for("booking"))

    if service_type not in [
        "Car Only",
        "Driver Only",
        "Car + Driver"
    ]:

        flash("Please select a valid service.")

        return redirect(url_for("booking"))

    if not start_date or not end_date:

        flash("Please select both start and end dates.")

        return redirect(url_for("booking"))

    # -------------------------
    # SERVICE SELECTION
    # -------------------------

    if service_type == "Car Only":

        driver_id = None

        if not car_id:

            flash("Please select a car.")

            return redirect(url_for("booking"))

    elif service_type == "Driver Only":

        car_id = None

        if not driver_id:

            flash("Please select a driver.")

            return redirect(url_for("booking"))

    elif service_type == "Car + Driver":

        if not car_id or not driver_id:

            flash(
                "Please select both a car and a driver."
            )

            return redirect(url_for("booking"))

    # -------------------------
    # CALCULATE TOTAL PRICE
    # -------------------------

    total_price = calculate_total_price(
        service_type,
        car_id,
        driver_id,
        start_date,
        end_date
    )

    if total_price is None:

        flash(
            "Invalid booking details. "
            "Please check your dates and selected vehicle/driver."
        )

        return redirect(url_for("booking"))

    # -------------------------
    # GET CAR NAME
    # -------------------------

    car_name = None

    if car_id:

        for car in cars:

            if str(car["car_id"]) == str(car_id):

                car_name = car["car_model"]

                break

    # -------------------------
    # GET DRIVER NAME
    # -------------------------

    driver_name = None

    if driver_id:

        for driver in drivers:

            if str(driver["driver_id"]) == str(driver_id):

                driver_name = driver["name"]

                break

    # -------------------------
    # SHOW BOOKING SUMMARY
    # -------------------------

    return render_template(
        "booking_summary.html",

        service_type=service_type,

        pickup_location=pickup_location,

        destination=destination,

        start_date=start_date,

        end_date=end_date,

        car_id=car_id,

        driver_id=driver_id,

        car_name=car_name,

        driver_name=driver_name,

        total_price=total_price
    )


# -------------------------
# CONFIRM BOOKING
# -------------------------

@app.route(
    "/booking/confirm",
    methods=["POST"]
)
def confirm_booking():

    # -------------------------
    # LOGIN REQUIRED
    # -------------------------

    if "user_id" not in session:

        flash("Please login first.")

        return redirect(url_for("login"))

    # -------------------------
    # GET FORM DATA
    # -------------------------

    pickup_location = request.form.get(
        "pickup_location",
        ""
    ).strip()

    destination = request.form.get(
        "destination",
        ""
    ).strip()

    service_type = request.form.get(
        "service_type"
    )

    car_id = request.form.get(
        "car_id"
    ) or None

    driver_id = request.form.get(
        "driver_id"
    ) or None

    start_date = request.form.get(
        "start_date"
    )

    end_date = request.form.get(
        "end_date"
    )

    # -------------------------
    # BASIC VALIDATION
    # -------------------------

    if not pickup_location or not destination:

        flash(
            "Pickup location and destination are required."
        )

        return redirect(url_for("booking"))

    if service_type not in [
        "Car Only",
        "Driver Only",
        "Car + Driver"
    ]:

        flash("Invalid service selected.")

        return redirect(url_for("booking"))

    if not start_date or not end_date:

        flash("Please select valid booking dates.")

        return redirect(url_for("booking"))

    # -------------------------
    # VALIDATE SELECTIONS
    # -------------------------

    if service_type == "Car Only":

        driver_id = None

        if not car_id:

            flash("Please select a car.")

            return redirect(url_for("booking"))

    elif service_type == "Driver Only":

        car_id = None

        if not driver_id:

            flash("Please select a driver.")

            return redirect(url_for("booking"))

    elif service_type == "Car + Driver":

        if not car_id or not driver_id:

            flash(
                "Please select both a car and a driver."
            )

            return redirect(url_for("booking"))

    # -------------------------
    # RECALCULATE TOTAL PRICE
    # -------------------------

    total_price = calculate_total_price(
        service_type,
        car_id,
        driver_id,
        start_date,
        end_date
    )

    if total_price is None:

        flash(
            "Invalid booking details. "
            "Please check your dates and selections."
        )

        return redirect(url_for("booking"))

    # -------------------------
    # CREATE BOOKING
    # -------------------------

    try:

        booking_id = create_booking(
            session["user_id"],
            car_id,
            driver_id,
            pickup_location,
            destination,
            start_date,
            end_date,
            service_type,
            total_price
        )

    except Exception as e:

        print("Booking creation error:", e)

        flash(
            "Unable to create your booking. "
            "Please try again."
        )

        return redirect(url_for("booking"))

    # -------------------------
    # BOOKING SUCCESS
    # -------------------------

    return render_template(
        "booking_success.html",

        booking_id=booking_id,

        pickup_location=pickup_location,

        destination=destination
    )


# -------------------------
# MY BOOKINGS
# -------------------------

@app.route("/my-bookings")
def my_bookings():

    if "user_id" not in session:

        flash("Please login first.")

        return redirect(url_for("login"))

    connection = None

    try:

        connection = get_connection()

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    b.booking_id,
                    b.pickup_location,
                    b.destination,
                    b.start_date,
                    b.end_date,
                    b.service_type,
                    b.total_price,
                    b.booking_status,
                    c.car_model,
                    c.car_number,
                    d.name AS driver_name
                FROM bookings b
                LEFT JOIN cars c
                    ON b.car_id = c.car_id
                LEFT JOIN drivers d
                    ON b.driver_id = d.driver_id
                WHERE b.user_id = %s
                ORDER BY b.booking_id DESC
                """,
                (
                    session["user_id"],
                )
            )

            bookings = cursor.fetchall()

        return render_template(
            "my_bookings.html",
            bookings=bookings
        )

    except Exception as e:

        print("My bookings error:", e)

        flash("Unable to load your bookings.")

        return render_template(
            "my_bookings.html",
            bookings=[]
        )

    finally:

        if connection:
            connection.close()


# -------------------------
# CANCEL BOOKING
# -------------------------

@app.route("/cancel-booking/<int:booking_id>")
def cancel_booking(booking_id):

    if "user_id" not in session:

        flash("Please login first.")

        return redirect(url_for("login"))

    connection = None

    try:

        connection = get_connection()

        with connection.cursor() as cursor:

            # Make sure the booking belongs
            # to the logged-in user

            cursor.execute(
                """
                SELECT booking_id
                FROM bookings
                WHERE booking_id = %s
                AND user_id = %s
                """,
                (
                    booking_id,
                    session["user_id"]
                )
            )

            booking = cursor.fetchone()

            if not booking:

                flash(
                    "Booking not found or you are not authorized."
                )

                return redirect(
                    url_for("my_bookings")
                )

            # Cancel the booking

            cursor.execute(
                """
                UPDATE bookings
                SET booking_status = 'cancelled'
                WHERE booking_id = %s
                AND user_id = %s
                """,
                (
                    booking_id,
                    session["user_id"]
                )
            )

            connection.commit()

        flash(
            f"Booking #{booking_id} cancelled."
        )

    except Exception as e:

        if connection:
            connection.rollback()

        print("Cancellation error:", e)

        flash(
            "Unable to cancel booking."
        )

    finally:

        if connection:
            connection.close()

    return redirect(
        url_for("my_bookings")
    )


# -------------------------
# RUN APPLICATION
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)