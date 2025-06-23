from flask import Flask, request, jsonify, send_file  # Agregamos send_file
from flask_cors import CORS
import pymongo
from pymongo import MongoClient
from bson import ObjectId
import base64
from io import BytesIO
from PIL import Image
import gridfs
import io  # Agregamos io

app = Flask(__name__)

# Configuración de CORS para permitir solicitudes desde cualquier origen
CORS(app, origins=["http://3.212.132.24:8080"], supports_credentials=True)

# Conexión a MongoDB en Docker local aaa
client = MongoClient("mongodb://admin:admin123@mongo-db:27017/CatalogServiceDB?authSource=admin")
db = client["CatalogServiceDB"]
fs = gridfs.GridFS(db)

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        # Verificamos si hay un archivo y el 'model_id' en el formulario
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        if 'model_id' not in request.form:
            return jsonify({"error": "Model ID is required"}), 400

        # Obtenemos los datos del archivo y el 'model_id' de la solicitud
        image_file = request.files['image']
        model_id = request.form['model_id']  # Usamos el model_id como el nombre del archivo

        # Guardamos la imagen en GridFS
        image_data = image_file.read()
        file_id = fs.put(image_data, filename=f"{model_id}.jpg")  # Usamos el model_id como nombre

        # Guardamos la referencia de la imagen en la colección
        image_doc = {
            "name": f"{model_id}.jpg",
            "image_id": str(file_id),
            "model_id": model_id  # También guardamos el model_id en la base de datos
        }
        db.images.insert_one(image_doc)

        return jsonify({"message": "Image uploaded successfully", "image_id": str(file_id)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/images', methods=['GET'])
def get_images():
    try:
        images = list(db.images.find({}, {"_id": 0}))  # Obtener todas las imágenes
        return jsonify({"images": images}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/image/<model_id>', methods=['GET'])
def get_image_by_model_id(model_id):
    try:
        # Buscar la referencia de la imagen en la colección
        image_doc = db.images.find_one({"model_id": model_id})
        if not image_doc:
            return jsonify({"error": "Image not found"}), 404

        # Obtener la imagen de GridFS usando `image_id`
        image_id = image_doc["image_id"]
        image_file = fs.get(ObjectId(image_id))  # Convertimos a ObjectId

        # Enviar la imagen como respuesta
        return send_file(io.BytesIO(image_file.read()), mimetype='image/jpeg')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5009)