def get_route(pickup, destination):
    """
    Get route information between pickup and destination.

    This function will later connect to the GeoMap API.
    """

    return {
        "pickup": pickup,
        "destination": destination,
        "distance": None,
        "duration": None,
        "route": None
    }