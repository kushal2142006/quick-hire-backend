import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import cursor, db
import bcrypt
from dotenv import load_dotenv
import traceback

load_dotenv()

app = Flask(__name__)
CORS(app)

# ✅ Get port from environment or default to 5000
PORT = int(os.getenv('PORT', 5000))

# =========================
# HOME ENDPOINT
# =========================

@app.route("/")
def home():
    return jsonify({
        "status": "success",
        "message": "QuickHire Backend Running ✅"
    })

# =========================
# SIGNUP ENDPOINT
# =========================

@app.route("/api/auth/signup", methods=["POST"])
def signup():
    try:
        data = request.json
        print("📝 Signup Request Data:", data)

        # Validate input
        if not all([data.get("name"), data.get("email"), data.get("password")]):
            return jsonify({
                "status": "error",
                "message": "Name, email, and password are required"
            }), 400

        # Check if email already exists
        try:
            cursor.execute("SELECT * FROM users WHERE email=?", (data["email"],))
            if cursor.fetchone():
                return jsonify({
                    "status": "error",
                    "message": "Email already registered"
                }), 400
        except Exception as db_error:
            print("❌ Database Check Error:", db_error)
            raise

        # Hash password
        hashed_password = bcrypt.hashpw(
            data["password"].encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # Insert user
        query = """
        INSERT INTO users (name, email, phone, password, role)
        VALUES (?, ?, ?, ?, ?)
        """
        
        values = (
            data["name"],
            data["email"],
            data.get("phone", ""),
            hashed_password,
            data.get("role", "user")
        )

        print("🔍 Query:", query)
        print("📊 Values:", values)

        cursor.execute(query, values)
        db.commit()
        print("✅ User inserted successfully!")

        return jsonify({
            "status": "success",
            "message": "User registered successfully"
        }), 201

    except Exception as e:
        print("❌ SIGNUP ERROR:", str(e))
        print("❌ ERROR TYPE:", type(e))
        print("❌ TRACEBACK:", traceback.format_exc())
        
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# =========================
# LOGIN ENDPOINT
# =========================

@app.route("/api/auth/login", methods=["POST"])
def login():
    try:
        data = request.json

        # Validate input
        if not data.get("email") or not data.get("password"):
            return jsonify({
                "status": "error",
                "message": "Email and password required"
            }), 400

        # Get user
        cursor.execute("SELECT * FROM users WHERE email=?", (data["email"],))
        user = cursor.fetchone()

        if not user:
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 404

        # Verify password
        if not bcrypt.checkpw(
            data["password"].encode("utf-8"),
            user["password"].encode("utf-8")
        ):
            return jsonify({
                "status": "error",
                "message": "Invalid password"
            }), 401

        return jsonify({
            "status": "success",
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        }), 200

    except Exception as e:
        print("❌ LOGIN ERROR:", str(e))
        print("❌ TRACEBACK:", traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# =========================
# GET ALL SERVICES
# =========================

@app.route("/api/services", methods=["GET"])
def get_services():
    try:
        cursor.execute("""
            SELECT s.*, u.name as provider_name 
            FROM services s 
            JOIN users u ON s.provider_id = u.id
        """)
        services = cursor.fetchall()

        return jsonify({
            "status": "success",
            "services": services
        }), 200

    except Exception as e:
        print("❌ GET SERVICES ERROR:", str(e))
        print("❌ TRACEBACK:", traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# =========================
# ADD SERVICE (Provider)
# =========================

@app.route("/api/services/add", methods=["POST"])
def add_service():
    try:
        data = request.json

        if not all([data.get("provider_id"), data.get("service_name"), data.get("price")]):
            return jsonify({
                "status": "error",
                "message": "Provider ID, service name, and price required"
            }), 400

        query = """
        INSERT INTO services (provider_id, service_name, description, price)
        VALUES (?, ?, ?, ?)
        """

        values = (
            data["provider_id"],
            data["service_name"],
            data.get("description", ""),
            data["price"]
        )

        cursor.execute(query, values)
        db.commit()

        return jsonify({
            "status": "success",
            "message": "Service added successfully"
        }), 201

    except Exception as e:
        print("❌ ADD SERVICE ERROR:", str(e))
        print("❌ TRACEBACK:", traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# =========================
# CREATE BOOKING
# =========================

@app.route("/api/bookings/create", methods=["POST"])
def create_booking():
    try:
        data = request.json

        required = ["user_id", "provider_id", "service_id", "booking_date", "booking_time", "address"]
        if not all(data.get(field) for field in required):
            return jsonify({
                "status": "error",
                "message": "All fields required"
            }), 400

        query = """
        INSERT INTO bookings (user_id, provider_id, service_id, booking_date, booking_time, address, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        values = (
            data["user_id"],
            data["provider_id"],
            data["service_id"],
            data["booking_date"],
            data["booking_time"],
            data["address"],
            "pending"
        )

        cursor.execute(query, values)
        db.commit()

        return jsonify({
            "status": "success",
            "message": "Booking created successfully"
        }), 201

    except Exception as e:
        print("❌ CREATE BOOKING ERROR:", str(e))
        print("❌ TRACEBACK:", traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# =========================
# GET USER BOOKINGS
# =========================

@app.route("/api/bookings/user/<int:user_id>", methods=["GET"])
def get_user_bookings(user_id):
    try:
        cursor.execute("""
            SELECT b.*, s.service_name, u.name as provider_name
            FROM bookings b
            JOIN services s ON b.service_id = s.id
            JOIN users u ON b.provider_id = u.id
            WHERE b.user_id=?
        """, (user_id,))
        
        bookings = cursor.fetchall()

        return jsonify({
            "status": "success",
            "bookings": bookings
        }), 200

    except Exception as e:
        print("❌ GET USER BOOKINGS ERROR:", str(e))
        print("❌ TRACEBACK:", traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# =========================
# GET PROVIDER BOOKINGS
# =========================

@app.route("/api/bookings/provider/<int:provider_id>", methods=["GET"])
def get_provider_bookings(provider_id):
    try:
        cursor.execute("""
            SELECT b.*, s.service_name, u.name as customer_name
            FROM bookings b
            JOIN services s ON b.service_id = s.id
            JOIN users u ON b.user_id = u.id
            WHERE b.provider_id=?
        """, (provider_id,))
        
        bookings = cursor.fetchall()

        return jsonify({
            "status": "success",
            "bookings": bookings
        }), 200

    except Exception as e:
        print("❌ GET PROVIDER BOOKINGS ERROR:", str(e))
        print("❌ TRACEBACK:", traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# =========================
# SEND MESSAGE
# =========================

@app.route("/api/messages/send", methods=["POST"])
def send_message():
    try:
        data = request.json

        if not all([data.get("sender_id"), data.get("receiver_id"), data.get("message")]):
            return jsonify({
                "status": "error",
                "message": "Sender ID, receiver ID, and message required"
            }), 400

        query = """
        INSERT INTO messages (sender_id, receiver_id, message)
        VALUES (?, ?, ?)
        """

        values = (
            data["sender_id"],
            data["receiver_id"],
            data["message"]
        )

        cursor.execute(query, values)
        db.commit()

        return jsonify({
            "status": "success",
            "message": "Message sent"
        }), 201

    except Exception as e:
        print("❌ SEND MESSAGE ERROR:", str(e))
        print("❌ TRACEBACK:", traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# =========================
# GET CHAT MESSAGES
# =========================

@app.route("/api/messages/chat/<int:user1>/<int:user2>", methods=["GET"])
def get_chat(user1, user2):
    try:
        cursor.execute("""
            SELECT * FROM messages
            WHERE (sender_id=? AND receiver_id=?)
            OR (sender_id=? AND receiver_id=?)
            ORDER BY id ASC
        """, (user1, user2, user2, user1))
        
        messages = cursor.fetchall()

        return jsonify({
            "status": "success",
            "messages": messages
        }), 200

    except Exception as e:
        print("❌ GET CHAT ERROR:", str(e))
        print("❌ TRACEBACK:", traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 QuickHire Backend Starting...")
    print("="*50)
    print(f"📍 Server running on: 0.0.0.0:{PORT}")
    print("📍 API Base URL: /api/")
    print("="*50 + "\n")
    
    app.run(debug=False, host="0.0.0.0", port=PORT)
