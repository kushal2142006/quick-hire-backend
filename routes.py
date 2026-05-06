from flask import Blueprint, request, jsonify
from database import cursor, db
from models import UserModel, ServiceModel, BookingModel

# Create blueprints
user_routes = Blueprint("users", __name__, url_prefix="/api/users")
service_routes = Blueprint("services", __name__, url_prefix="/api/services")
booking_routes = Blueprint("bookings", __name__, url_prefix="/api/bookings")

# User routes
@user_routes.route("/<int:user_id>")
def get_user(user_id):
    user = UserModel.get_user_by_id(user_id)
    if user:
        user.pop("password")  # Remove password
        return jsonify({"status": "success", "user": user}), 200
    return jsonify({"status": "error", "message": "User not found"}), 404

# Service routes
@service_routes.route("/provider/<int:provider_id>")
def get_provider_services(provider_id):
    services = ServiceModel.get_provider_services(provider_id)
    return jsonify({"status": "success", "services": services}), 200

# Booking routes
@booking_routes.route("/<int:booking_id>/status", methods=["PUT"])
def update_booking_status(booking_id):
    data = request.json
    BookingModel.update_booking_status(booking_id, data["status"])
    return jsonify({"status": "success", "message": "Status updated"}), 200
