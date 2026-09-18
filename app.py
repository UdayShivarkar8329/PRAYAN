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
                    (name, email, phone, password_hash)
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

    destination = request.args.get("destination")

    if not destination:
        return "Please enter a destination."

    result = get_route("Amravati", destination)

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
                SELECT car_id, car_number, car_model,
                       car_type, seats, price_per_day,
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
                SELECT driver_id, name, phone,
                       license_number, experience,
                       price_per_day, availability_status
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

    if "user_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    destination = request.args.get("destination", "")

    if request.method == "POST":
        pickup_location = request.form.get("pickup_location", "").strip()
        destination = request.form.get("destination", "").strip()
        service_type = request.form.get("service_type", "")
        car_id = request.form.get("car_id")
        driver_id = request.form.get("driver_id")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        validation_error = None

        # -------------------------
        # VALIDATION
        # -------------------------
        if not pickup_location:
            validation_error = "Pickup location is required."
        elif not destination:
            validation_error = "Destination is required."
        elif not destination:
            validation_error = "Destination is required."

        elif destination.lower() == "amravati":
            validation_error = "Destination must be different from pickup location."

        elif service_type not in [
            "Car Only",
            "Driver Only",
            "Car + Driver"
        ]:
            validation_error = "Please select a valid service type."

        elif not start_date or not end_date:
            validation_error = "Start date and end date are required."

        elif end_date < start_date:
            validation_error = "End date cannot be before start date."

        elif service_type == "Car Only" and not car_id:
            validation_error = "Please select a car."

        elif service_type == "Driver Only" and not driver_id:
            validation_error = "Please select a driver."

        elif service_type == "Car + Driver" and (not car_id or not driver_id):
            validation_error = "Please select both a car and a driver."

        # -------------------------
        # IF VALIDATION FAILED
        # -------------------------

        if validation_error:
            flash(validation_error)

        else:

            # Remove unused vehicle/driver
            if service_type == "Car Only":
                driver_id = None

            elif service_type == "Driver Only":
                car_id = None

            # -------------------------
            # CALCULATE PRICE
            # -------------------------

            try:

                total_price = calculate_total_price(
                    service_type,
                    car_id,
                    driver_id,
                    start_date,
                    end_date
                )

                if total_price is None:

                    flash(
                        "Selected car or driver is unavailable."
                    )

                else:

                    # -------------------------
                    # CREATE BOOKING
                    # -------------------------

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

                    flash(
                        f"Booking #{booking_id} confirmed successfully!"
                    )

                    return redirect(
                        url_for("my_bookings")
                    )

            except Exception as e:

                print("Booking error:", e)

                flash(
                    "Unable to create booking."
                )

    # -------------------------
    # LOAD AVAILABLE CARS/DRIVERS
    # -------------------------

    try:

        cars_list = get_available_cars()
        drivers_list = get_available_drivers()

    except Exception as e:

        print("Loading booking data error:", e)

        cars_list = []
        drivers_list = []

        flash(
            "Unable to load cars or drivers."
        )

    return render_template(
        "booking.html",
        destination=destination,
        cars=cars_list,
        drivers=drivers_list
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
                (session["user_id"],)
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

            # Make sure this booking belongs to the
            # currently logged-in user
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