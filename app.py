from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from maps.maps import get_route
import uuid


app = Flask(__name__)

# Demo secret key for the MVP frontend.
# A production application should use an environment variable.
app.secret_key = "prayan-demo-secret-key"


# ---------------------------------------------------------
# Demo data
# ---------------------------------------------------------

CARS = [
    {
        "id": 1,
        "name": "Maruti Ertiga",
        "type": "SUV",
        "seats": 7,
        "price": 2200
    },
    {
        "id": 2,
        "name": "Maruti Swift",
        "type": "Hatchback",
        "seats": 5,
        "price": 1600
    },
    {
        "id": 3,
        "name": "Mahindra Scorpio",
        "type": "SUV",
        "seats": 7,
        "price": 2500
    }
]


DRIVERS = [
    {
        "id": 1,
        "name": "Rahul Patil",
        "experience": "5+ years",
        "price": 1200
    },
    {
        "id": 2,
        "name": "Akash Sharma",
        "experience": "7+ years",
        "price": 1400
    },
    {
        "id": 3,
        "name": "Vijay Deshmukh",
        "experience": "4+ years",
        "price": 1100
    }
]


# Demo booking storage.
# This is temporary until the database integration is completed.
bookings = []


# ---------------------------------------------------------
# Home
# ---------------------------------------------------------

@app.route("/")
def home():
    return render_template("home.html")


# ---------------------------------------------------------
# Route / Map
# ---------------------------------------------------------

@app.route("/route")
def route():
    destination = request.args.get("destination")

    if not destination:
        return jsonify({
            "error": "Please enter a destination."
        }), 400

    result = get_route("Amravati", destination)

    return jsonify(result)


# ---------------------------------------------------------
# Cars
# ---------------------------------------------------------

@app.route("/cars")
def cars():
    return render_template(
        "cars.html",
        cars=CARS
    )


# ---------------------------------------------------------
# Drivers
# ---------------------------------------------------------

@app.route("/drivers")
def drivers():
    return render_template(
        "drivers.html",
        drivers=DRIVERS
    )


# ---------------------------------------------------------
# Booking
# ---------------------------------------------------------

@app.route("/booking", methods=["GET", "POST"])
def booking():

    if request.method == "POST":

        service_type = request.form.get("service_type")
        pickup_location = request.form.get("pickup_location")
        destination = request.form.get("destination")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        car_id = request.form.get("car_id")
        driver_id = request.form.get("driver_id")

        car_name = None
        driver_name = None

        for car in CARS:
            if str(car["id"]) == str(car_id):
                car_name = car["name"]
                break

        for driver in DRIVERS:
            if str(driver["id"]) == str(driver_id):
                driver_name = driver["name"]
                break

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
            driver_name=driver_name
        )

    # GET request

    return render_template(
        "booking.html",
        destination=request.args.get("destination"),
        service_type=request.args.get("service_type"),
        pickup_location="Amravati",
        car_id=request.args.get("car_id"),
        driver_id=request.args.get("driver_id")
    )


# ---------------------------------------------------------
# Confirm Booking
# ---------------------------------------------------------

@app.route("/booking/confirm", methods=["POST"])
def confirm_booking():

    service_type = request.form.get("service_type")
    pickup_location = request.form.get("pickup_location")
    destination = request.form.get("destination")
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    car_id = request.form.get("car_id")
    driver_id = request.form.get("driver_id")

    car_name = None
    driver_name = None

    for car in CARS:
        if str(car["id"]) == str(car_id):
            car_name = car["name"]
            break

    for driver in DRIVERS:
        if str(driver["id"]) == str(driver_id):
            driver_name = driver["name"]
            break

    booking_id = str(uuid.uuid4())[:8].upper()

    booking_data = {
        "id": booking_id,
        "service_type": service_type,
        "pickup_location": pickup_location,
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "car_id": car_id,
        "driver_id": driver_id,
        "car_name": car_name,
        "driver_name": driver_name,
        "status": "Confirmed"
    }

    bookings.append(booking_data)

    return render_template(
        "booking_success.html",
        booking_id=booking_id,
        pickup_location=pickup_location,
        destination=destination
    )


# ---------------------------------------------------------
# My Bookings / Dashboard
# ---------------------------------------------------------

@app.route("/my-bookings")
def my_bookings():
    return render_template(
        "dashboard.html",
        bookings=bookings
    )


# ---------------------------------------------------------
# Cancel Booking
# ---------------------------------------------------------

@app.route("/cancel-booking/<booking_id>")
def cancel_booking(booking_id):

    for booking in bookings:

        if str(booking["id"]) == str(booking_id):
            booking["status"] = "Cancelled"
            break

    return redirect(url_for("my_bookings"))


# ---------------------------------------------------------
# Login
# ---------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")

        session["user"] = email

        return redirect(url_for("my_bookings"))

    return render_template("login.html")


# ---------------------------------------------------------
# Register
# ---------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")

        session["user"] = {
            "name": name,
            "email": email,
            "phone": phone
        }

        return redirect(url_for("my_bookings"))

    return render_template("register.html")


# ---------------------------------------------------------
# Run application
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)