import grpc
import image_service_pb2
import image_service_pb2_grpc
from flask import Flask, jsonify, request
from pymongo import MongoClient
import jwt
from functools import wraps
from flask_cors import CORS
from dotenv import load_dotenv
import os
from bson import ObjectId
import urllib.parse

load_dotenv()

app = Flask(__name__)
# CORS(app)

# Enable CORS to allow requests from localhost:8080
# CORS(app, origins=["http://3.212.132.24:8080"], supports_credentials=True)

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["CatalogServiceDB"]
models_collection = db["models"]  # Collection to store 3D models

# Secret key for JWT
SECRET_KEY = os.getenv("SECRET_KEY")

# Function to decode JWT token and get user_id
def get_user_info_from_token():
    token = request.headers.get('Authorization')
    if not token:
        return None, None
    try:
        token = token.split(" ")[1]  # Asume que el token está precedido por "Bearer"
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
        user_id = decoded.get('user_id')
        user_name = decoded.get('username')  # Extrae el username del token
        print(f"Decoded token: user_id={user_id}, username={user_name}")  # Agregar esta línea para ver los valores
        return user_id, user_name
    except jwt.PyJWTError as e:
        print(f"JWT Error: {str(e)}")
        return None, None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, None

# Middleware to check if the current user is the owner of the model
def check_model_owner(model_id):
    user_id, user_name = get_user_info_from_token()
    print(f"User extracted from token: {user_name}")
    if not user_name:  # Aquí debería verificar el nombre de usuario, no el user_id
        return None
    model = models_collection.find_one({"_id": model_id})
    if model:
        print(f"Model created_by: {model.get('created_by')}")
        if model.get('created_by') == user_name:  # Compara user_name con created_by
            return user_name
    return None

# Test route
@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Catalog Service!"})

# Conectar al servicio gRPC
channel = grpc.insecure_channel("grpc-image-del-service:5014")
stub = image_service_pb2_grpc.ImageServiceStub(channel)

# Route to delete a 3D model by its name
@app.route("/models/<string:model_name>", methods=["DELETE"])
def delete_model(model_name):
    try:
        model_name = urllib.parse.unquote(model_name)
        print(f"🔍 Intentando eliminar modelo: '{model_name}'")
        
        model = models_collection.find_one({"name": model_name})
        if not model:
            return jsonify({"error": "Model not found"}), 404
        user_name = check_model_owner(model['_id'])  # Pasar _id, no user_id
        if not user_name:
            return jsonify({"error": "Unauthorized"}), 403  # Only owner can delete 3
        result = models_collection.delete_one({"name": model_name})
        if result.deleted_count > 0:
            return jsonify({"message": "Model deleted successfully"}), 200
        else:
            return jsonify({"error": "Error deleting model"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to delete a 3D model by its ID 2
@app.route("/models/id/<string:model_id>", methods=["DELETE"])
def delete_model_by_id(model_id):
    try:
        # Buscar el modelo por _id (convertido a ObjectId)
        model = models_collection.find_one({"_id": ObjectId(model_id)})
        if not model:
            return jsonify({"error": "Model not found"}), 404
        user_name = check_model_owner(model['_id'])  # Pasar _id, no user_id
        if not user_name:
            return jsonify({"error": "Unauthorized"}), 403  # Only owner can delete
        
        # Eliminar la imagen asociada al modelo usando gRPC
        response = stub.DeleteImageByModelId(image_service_pb2.DeleteImageRequest(model_id=model_id))

        # Verificar la respuesta de la eliminación de la imagen
        if not response.success:
            return jsonify({"error": "Error deleting image"}), 500
        
        result = models_collection.delete_one({"_id": ObjectId(model_id)})
        if result.deleted_count > 0:
            return jsonify({"message": "Model deleted successfully"}), 200
        else:
            return jsonify({"error": "Error deleting model"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    try:
        # Check MongoDB connection on startup
        client.admin.command("ping")
        print("Connected to MongoDB Atlas")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
    app.run(debug=True, host='0.0.0.0', port=5011)