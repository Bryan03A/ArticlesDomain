from flask import Flask, jsonify, request
from pymongo import MongoClient
import jwt
from flask_cors import CORS
from dotenv import load_dotenv
import os
from bson import ObjectId
import grpc
import image_service_pb2
import image_service_pb2_grpc

load_dotenv()

app = Flask(__name__)
# CORS(app)

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["CatalogServiceDB"]
models_collection = db["models"]  # Collection to store 3D models

# Secret key for JWT
SECRET_KEY = os.getenv("SECRET_KEY")

# Setup gRPC client (ajusta 'image-service' si tu contenedor tiene otro nombre)
channel = grpc.insecure_channel("image-service:5014")
stub = image_service_pb2_grpc.ImageServiceStub(channel)

def get_user_info_from_token():
    token = request.headers.get('Authorization')
    if not token:
        return None, None
    try:
        token = token.split(" ")[1]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
        user_id = decoded.get('user_id')
        user_name = decoded.get('username')
        print(f"Decoded token: user_id={user_id}, username={user_name}")
        return user_id, user_name
    except jwt.PyJWTError as e:
        print(f"JWT Error: {str(e)}")
        return None, None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, None

def check_model_owner(model_id):
    user_id, user_name = get_user_info_from_token()
    print(f"User extracted from token: {user_name}")
    if not user_name:
        return None
    model = models_collection.find_one({"_id": model_id})
    if model:
        print(f"Model created_by: {model.get('created_by')}")
        if model.get('created_by') == user_name:
            return user_name
    return None

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Catalog Service!"})

@app.route("/models", methods=["POST"])
def add_model():
    try:
        model_data = request.json
        print("Received model data:", model_data)

        user_id, user_name = get_user_info_from_token()
        if not user_id:
            return jsonify({"error": "Unauthorized, no token provided"}), 401
        if not user_name:
            return jsonify({"error": "User name not found in token"}), 401
        
        model_data['created_by'] = user_name
        result = models_collection.insert_one(model_data)
        model_id = str(result.inserted_id)

        return jsonify({"message": "Model added successfully", "model_id": model_id}), 201

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route("/models", methods=["GET"])
def get_models():
    try:
        models = list(models_collection.find({}))
        for model in models:
            model["_id"] = str(model["_id"])
        return jsonify({"models": models}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/models/user/<string:user_id>", methods=["GET"])
def get_models_by_user(user_id):
    try:
        models = list(models_collection.find({"created_by": user_id}))
        for model in models:
            model["_id"] = str(model["_id"])
        return jsonify({"models": models}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/models/<string:model_name>", methods=["GET"])
def get_model(model_name):
    try:
        model = models_collection.find_one({"name": model_name})
        if model:
            model["_id"] = str(model["_id"])
            return jsonify({"model": model}), 200
        else:
            return jsonify({"error": "Model not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/models/id/<string:model_id>", methods=["GET"])
def get_model_by_id(model_id):
    try:
        model = models_collection.find_one({"_id": ObjectId(model_id)}, {"_id": 0})
        if model:
            model["model_id"] = model_id
            return jsonify({"model": model}), 200
        else:
            return jsonify({"error": "Model not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/models/<string:model_name>", methods=["PUT"])
def update_model(model_name):
    try:
        model = models_collection.find_one({"name": model_name})
        if not model:
            return jsonify({"error": "Model not found"}), 404
        if not check_model_owner(model['_id']):
            return jsonify({"error": "Unauthorized"}), 403
        updated_data = request.json
        result = models_collection.update_one({"name": model_name}, {"$set": updated_data})
        if result.modified_count > 0:
            return jsonify({"message": "Model updated successfully"}), 200
        else:
            return jsonify({"error": "Error updating model"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/models/id/<string:model_id>", methods=["PUT"])
def update_model_by_id(model_id):
    try:
        model = models_collection.find_one({"_id": ObjectId(model_id)})
        if not model:
            return jsonify({"error": "Model not found"}), 404
        if not check_model_owner(model['_id']):
            return jsonify({"error": "Unauthorized"}), 403
        updated_data = request.json
        result = models_collection.update_one({"_id": ObjectId(model_id)}, {"$set": updated_data})
        if result.modified_count > 0:
            return jsonify({"message": "Model updated successfully"}), 200
        else:
            return jsonify({"error": "Error updating model"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Aquí integro la eliminación con gRPC para eliminar también la imagen relacionada
@app.route("/models/id/<string:model_id>", methods=["DELETE"])
def delete_model_by_id(model_id):
    try:
        model = models_collection.find_one({"_id": ObjectId(model_id)})
        if not model:
            return jsonify({"error": "Model not found"}), 404
        
        if not check_model_owner(model['_id']):
            return jsonify({"error": "Unauthorized"}), 403
        
        # Llamada gRPC para eliminar la imagen asociada
        response = stub.DeleteImageByModelId(image_service_pb2.DeleteImageRequest(model_id=model_id))
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
        client.admin.command("ping")
        print("Connected to MongoDB Atlas")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
    app.run(debug=True, host='0.0.0.0', port=5003)