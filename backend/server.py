from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime, timezone
import os
import uuid
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

# Initialize extensions
bcrypt = Bcrypt(app)
Session(app)
CORS(app, origins=os.environ.get('CORS_ORIGINS', '*').split(','), supports_credentials=True)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = MongoClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Collections
users_collection = db.users
products_collection = db.products
categories_collection = db.categories

# Initialize sample data
def init_sample_data():
    # Check if categories already exist
    if categories_collection.count_documents({}) == 0:
        categories = [
            {
                "id": str(uuid.uuid4()),
                "name": "Men's Wear",
                "image_url": "https://images.unsplash.com/photo-1618886614638-80e3c103d31a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzB8MHwxfHNlYXJjaHwxfHxtZW4lMjBmYXNoaW9ufGVufDB8fHx8MTc1OTgzOTI2M3ww&ixlib=rb-4.1.0&q=85",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Women's Wear",
                "image_url": "https://images.unsplash.com/photo-1617922001439-4a2e6562f328?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwxfHx3b21lbiUyMGZhc2hpb258ZW58MHx8fHwxNzU5ODcwOTg0fDA&ixlib=rb-4.1.0&q=85",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Children's Wear",
                "image_url": "https://images.unsplash.com/photo-1622218286192-95f6a20083c7?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwxfHxraWRzJTIwY2xvdGhpbmd8ZW58MHx8fHwxNzU5OTE5MjI5fDA&ixlib=rb-4.1.0&q=85",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Underwear",
                "image_url": "https://images.unsplash.com/photo-1568441556126-f36ae0900180?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHw0fHx1bmRlcndlYXJ8ZW58MHx8fHwxNzU5OTE5MjMzfDA&ixlib=rb-4.1.0&q=85",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        categories_collection.insert_many(categories)

    # Check if products already exist
    if products_collection.count_documents({}) == 0:
        categories_list = list(categories_collection.find({}))
        products = [
            {
                "id": str(uuid.uuid4()),
                "name": "Classic Cotton T-Shirt",
                "description": "Premium quality cotton t-shirt in multiple colors",
                "price": 29.99,
                "category_id": categories_list[0]["id"],
                "category_name": "Men's Wear",
                "image_url": "https://images.unsplash.com/photo-1562157873-818bc0726f68?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHwzfHxjbG90aGluZ3xlbnwwfHx8fDE3NTk4NTQyMTN8MA&ixlib=rb-4.1.0&q=85",
                "stock": 100,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Elegant Women's Dress",
                "description": "Beautiful and comfortable dress for all occasions",
                "price": 89.99,
                "category_id": categories_list[1]["id"],
                "category_name": "Women's Wear",
                "image_url": "https://images.unsplash.com/photo-1525507119028-ed4c629a60a3?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHwxfHxjbG90aGluZ3xlbnwwfHx8fDE3NTk4NTQyMTN8MA&ixlib=rb-4.1.0&q=85",
                "stock": 75,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Trendy Yellow Track Suit",
                "description": "Comfortable and stylish track suit perfect for casual wear",
                "price": 79.99,
                "category_id": categories_list[1]["id"],
                "category_name": "Women's Wear",
                "image_url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDJ8MHwxfHNlYXJjaHwxfHxmYXNoaW9ufGVufDB8fHx8MTc1OTkxOTI3MHww&ixlib=rb-4.1.0&q=85",
                "stock": 50,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Kids Colorful Collection",
                "description": "Vibrant and comfortable children's clothing collection",
                "price": 39.99,
                "category_id": categories_list[2]["id"],
                "category_name": "Children's Wear",
                "image_url": "https://images.unsplash.com/photo-1622218286192-95f6a20083c7?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwxfHxraWRzJTIwY2xvdGhpbmd8ZW58MHx8fHwxNzU5OTE5MjI5fDA&ixlib=rb-4.1.0&q=85",
                "stock": 60,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Professional Shirts Collection",
                "description": "High-quality professional shirts for office and formal wear",
                "price": 59.99,
                "category_id": categories_list[0]["id"],
                "category_name": "Men's Wear",
                "image_url": "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHw0fHxjbG90aGluZ3xlbnwwfHx8fDE3NTk4NTQyMTN8MA&ixlib=rb-4.1.0&q=85",
                "stock": 80,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Stylish Outerwear",
                "description": "Trendy coats and jackets for all seasons",
                "price": 149.99,
                "category_id": categories_list[1]["id"],
                "category_name": "Women's Wear",
                "image_url": "https://images.unsplash.com/photo-1571513800374-df1bbe650e56?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDJ8MHwxfHNlYXJjaHwzfHxmYXNoaW9ufGVufDB8fHx8MTc1OTkxOTI3MHww&ixlib=rb-4.1.0&q=85",
                "stock": 40,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        products_collection.insert_many(products)

# Routes

@app.route('/api/', methods=['GET'])
@app.route('/api', methods=['GET'])
def root():
    return jsonify({"message": "StyleSphere Fashion API"})

# Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate input
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({"error": "Username, email, and password are required"}), 400
        
        # Check if user already exists
        if users_collection.find_one({"email": data['email']}):
            return jsonify({"error": "User with this email already exists"}), 400
        
        if users_collection.find_one({"username": data['username']}):
            return jsonify({"error": "Username already taken"}), 400
        
        # Hash password and create user
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        
        user = {
            "id": str(uuid.uuid4()),
            "username": data['username'],
            "email": data['email'],
            "password": hashed_password,
            "full_name": data.get('full_name', ''),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        users_collection.insert_one(user)
        
        # Create session
        session['user_id'] = user['id']
        session['username'] = user['username']
        
        return jsonify({
            "message": "Registration successful",
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "full_name": user['full_name']
            }
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email and password are required"}), 400
        
        # Find user
        user = users_collection.find_one({"email": data['email']})
        
        if not user or not bcrypt.check_password_hash(user['password'], data['password']):
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Create session
        session['user_id'] = user['id']
        session['username'] = user['username']
        
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "full_name": user.get('full_name', '')
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logout successful"}), 200

@app.route('/api/profile', methods=['GET'])
def get_profile():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    user = users_collection.find_one({"id": session['user_id']}, {"password": 0, "_id": 0})
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({"user": user}), 200

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        data = request.get_json()
        
        # Prepare update data
        update_data = {}
        if 'full_name' in data:
            update_data['full_name'] = data['full_name']
        if 'email' in data:
            # Check if email already exists for another user
            existing_user = users_collection.find_one({
                "email": data['email'],
                "id": {"$ne": session['user_id']}
            })
            if existing_user:
                return jsonify({"error": "Email already in use"}), 400
            update_data['email'] = data['email']
        
        if update_data:
            users_collection.update_one(
                {"id": session['user_id']},
                {"$set": update_data}
            )
        
        # Return updated user
        user = users_collection.find_one({"id": session['user_id']}, {"password": 0, "_id": 0})
        return jsonify({"user": user}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Product Routes
@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        categories = list(categories_collection.find({}, {"_id": 0}))
        return jsonify({"categories": categories}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        category_id = request.args.get('category_id')
        
        query = {}
        if category_id:
            query['category_id'] = category_id
        
        products = list(products_collection.find(query, {"_id": 0}))
        return jsonify({"products": products}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = products_collection.find_one({"id": product_id}, {"_id": 0})
        
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        return jsonify({"product": product}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        user = users_collection.find_one({"id": session['user_id']}, {"password": 0, "_id": 0})
        return jsonify({"authenticated": True, "user": user}), 200
    else:
        return jsonify({"authenticated": False}), 200

# Initialize sample data on startup
with app.app_context():
    init_sample_data()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)