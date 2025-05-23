from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
import hashlib
import jwt
import os
from supabase import create_client
import bcrypt
from datetime import datetime, timedelta

app = Flask(__name__)

# Enable CORS for all routes and WebSocket connections
CORS(app, supports_credentials=True)

# Keep track of connected users by username and their session IDs
users = {}

def verify_jwt(token):
    try:
        decoded = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def generate_jwt(api_key):
    payload = {
        "sub": api_key,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=90),
    }
    return jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")

@app.route("/user/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()
        if "user_name" not in data:
            return jsonify({"status": "Register Failed", "error": "Username is required"}),400
        if "password" not in data: # Hash password in the back end for security
            return jsonify({"status": "Register Failed", "error": "Password is required"}),400
        if "email" not in data: # Hash password in the back end for security
            return jsonify({"status": "Register Failed", "error": "Password is required"}),400

        # Check pass and user name in database

        load_dotenv()

        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        response = supabase.table("User").select("*").eq("user_name", data["user_name"]).execute()

        if response.data:
            return jsonify({"status": "Register Failed", "error": "Username found. Please Login!"}),400
        
        password = data["password"].encode("utf-8")
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())

        data_reg = {
            "user_name": data["user_name"],
            "hashed_password": hashed.decode("utf-8"),
            "email": data["email"],
            "user_token": generate_jwt("user_name")
        }

        response_register = supabase.table("User").insert(data_reg).execute()

        # Check the response
        if response_register.data:
            return jsonify({"status": "Register Success"}, 200)
        else:
            return jsonify({"status": "Register Failed", "error": "Try again later"}),500

    except Exception as e:
        return jsonify({"status": "Failed", "error": f"{str(e)}"}),500



@app.route("/reservation", methods=["POST"])
def post_reservation():
    try:
        data = request.get_json()
        if "user_id" not in data:
            return jsonify({"status": "Register Failed", "error": "User ID is required"}),400
        if "start_date" not in data: # Hash password in the back end for security
            return jsonify({"status": "Register Failed", "error": "Start Date is required"}),400
        if "end_date" not in data: # Hash password in the back end for security
            return jsonify({"status": "Register Failed", "error": "End Date is required"}),400
        if "status" not in data:
            return jsonify({"status": "Register Failed", "error": "Reservation Status is required"}),400


        # Validate date format
        try:
            start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
            end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        except ValueError:
             return jsonify({"status": "Register Failed", "error": "Dates must be in YYYY-MM-DD format"}), 400

        load_dotenv()
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        data_reservation = {
            "user_id": data["user_id"], 
            "start_date": start_date.isoformat(), 
            "end_date": end_date.isoformat(), 
            "status": data["status"] 
        }

        response = supabase.table("Reservation").insert(data_reservation).execute()
        
        if response.data:
            return jsonify({"status": "Success"}, 200)
        else:
            return jsonify({"status": "Reservation Failed", "error": "Try again later"}),500

    except Exception as e:
        return jsonify({"status": "Error", "error": f"{str(e)}"}),400

@app.route("/get/key", methods=["POST"])
def get_key():
    try:
        data = request.get_json()

        if "property_id" not in data: 
            return jsonify({"status": "Fetch Failed", "error": "Property ID is required"}), 400

        load_dotenv()
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        response = supabase.table("Key").select("*").eq("id", data["property_id"]).execute()
        
        if not response.data:
            return jsonify({"status": "Fetch Failed", "error": "No matching property ID found"}), 404
        
        key_value = response.data[0].get("current_key")  # Adjust field name if different

        return jsonify({
            "status": "Success",
            "property_id": data["property_id"],
            "key": key_value
        }), 200

    except Exception as e:
        return jsonify({"status": "Error", "error": str(e)}), 400

@app.route("/list/properties", methods=["GET"])
def get_properties(): 
    try:
        load_dotenv()
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.table("Properties").select("*").execute()
        
        if not response.data: 
            return jsonify({"status": "Fetch Failed", "error":"Failed to fetch key"})
        else: 
            return jsonify({"status":"Success", "list":response.data})
    except Exception as e:
        return jsonify({"status": "Error", "error": f"{str(e)}"}),400

@app.route("/user/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        if "user_name" not in data:
            return jsonify({"status": "Login Failed", "error": "Username is required"}),200
        if "password" not in data:
            return jsonify({"status": "Login Failed", "error": "Password is required"}),200

        # Check pass and user name in database

        load_dotenv()

        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        response = supabase.table("User").select("*").eq("user_name", data["user_name"]).execute()
        
        if not response.data:
            return jsonify({"status": "Login Failed", "error": "Username not found. Please register first!"}),200

        if bcrypt.checkpw(data["password"].encode("utf-8"), response.data[0]["hashed_password"].encode("utf-8")) : 
            username = data["user_name"]
            response = supabase.table("User") \
            .select("*") \
            .or_(f"sender.eq.{username},receiver.eq.{username}") \
            .order("timestamp", desc=False) \
            .execute()

            messages = response.data if response.data else []

            return jsonify({
                "status": "Login Success",
                "messages": messages
            }), 200

        # TODO: Add last login session in database
        return jsonify({"status": "Login Failed", "error": "Wrong password"}),200
    except Exception as e:
        return jsonify({"status": "Error", "error": f"{str(e)}"}),400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
