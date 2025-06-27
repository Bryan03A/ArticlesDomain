import grpc
import image_service_pb2
import image_service_pb2_grpc
from concurrent import futures
from pymongo import MongoClient
import gridfs
from bson import ObjectId
import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

# Leer configuración desde variables de entorno
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
MONGO_DB = os.getenv('MONGO_DB', 'CatalogServiceDB')
MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')

# Construir URI
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin"

# Conectar a MongoDB
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
fs = gridfs.GridFS(db)

class ImageService(image_service_pb2_grpc.ImageServiceServicer):
    def DeleteImageByModelId(self, request, context):
        try:
            model_id = request.model_id

            image_doc = db.images.find_one({"model_id": model_id})
            if not image_doc:
                return image_service_pb2.DeleteImageResponse(success=False, message="Image not found")

            image_id = image_doc["image_id"]
            fs.delete(ObjectId(image_id))
            db.images.delete_one({"model_id": model_id})

            return image_service_pb2.DeleteImageResponse(success=True, message="Image deleted successfully")

        except Exception as e:
            return image_service_pb2.DeleteImageResponse(success=False, message=str(e))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    image_service_pb2_grpc.add_ImageServiceServicer_to_server(ImageService(), server)
    server.add_insecure_port("0.0.0.0:5014")
    print("🔹 gRPC Image Service running on port 5014...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()