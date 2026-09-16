from flask import Flask, request, render_template
from maps.maps import get_route

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/route")
def route():
    destination = request.args.get("destination")

    if not destination:
        return "Please enter a destination."

    result = get_route("Amravati", destination)

    return result

@app.route("/booking")
def booking():
    destination = request.args.get("destination")

    return render_template(
        "booking.html",
        destination=destination
    )

if __name__ == "__main__":
    app.run(debug=True)