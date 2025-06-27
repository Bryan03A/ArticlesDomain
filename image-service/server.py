from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from PIL import Image
import gridfs
import io
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)
# CORS(app, origins=["http://3.212.132.24:8080"], supports_credentials=True)

# Obtener configuración desde .env
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
MONGO_DB = os.getenv('MONGO_DB', 'CatalogServiceDB')
MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')

# Construir la URI de conexión
mongo_uri = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin"

# Conectarse a MongoDB
client = MongoClient(mongo_uri)
db = client[MONGO_DB]
fs = gridfs.GridFS(db)

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        if 'model_id' not in request.form:
            return jsonify({"error": "Model ID is required"}), 400

        image_file = request.files['image']
        model_id = request.form['model_id']

        image_data = image_file.read()
        file_id = fs.put(image_data, filename=f"{model_id}.jpg")

        image_doc = {
            "name": f"{model_id}.jpg",
            "image_id": str(file_id),
            "model_id": model_id
        }
        db.images.insert_one(image_doc)

        return jsonify({"message": "Image uploaded successfully", "image_id": str(file_id)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/images', methods=['GET'])
def get_images():
    try:
        images = list(db.images.find({}, {"_id": 0}))
        return jsonify({"images": images}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/image/<model_id>', methods=['GET'])
def get_image_by_model_id(model_id):
    try:
        image_doc = db.images.find_one({"model_id": model_id})
        if not image_doc:
            return jsonify({"error": "Image not found"}), 404

        image_id = image_doc["image_id"]
        image_file = fs.get(ObjectId(image_id))

        return send_file(io.BytesIO(image_file.read()), mimetype='image/jpeg')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5009)