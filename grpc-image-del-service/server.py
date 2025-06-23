import grpc
import image_service_pb2
import image_service_pb2_grpc
from concurrent import futures
from pymongo import MongoClient
import gridfs
from bson import ObjectId

# URI corregida para MongoDB remoto en tu servidor Docker 2
MONGO_URI = "mongodb://admin:admin123@35.168.99.213:27017/CatalogServiceDB?authSource=admin"
client = MongoClient(MONGO_URI)
db = client["CatalogServiceDB"]
fs = gridfs.GridFS(db)

class ImageService(image_service_pb2_grpc.ImageServiceServicer):
    def DeleteImageByModelId(self, request, context):
        try:
            model_id = request.model_id

            # Buscar la imagen en la colección "images" aa
            image_doc = db.images.find_one({"model_id": model_id})
            if not image_doc:
                return image_service_pb2.DeleteImageResponse(success=False, message="Image not found")

            # Obtener el image_id y eliminarlo de GridFS
            image_id = image_doc["image_id"]
            fs.delete(ObjectId(image_id))

            # Eliminar la referencia en la colección "images"
            db.images.delete_one({"model_id": model_id})

            return image_service_pb2.DeleteImageResponse(success=True, message="Image deleted successfully")

        except Exception as e:
            return image_service_pb2.DeleteImageResponse(success=False, message=str(e))

# Iniciar el servidor gRPC
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    image_service_pb2_grpc.add_ImageServiceServicer_to_server(ImageService(), server)
    server.add_insecure_port("0.0.0.0:5014") # Puerto del servicio
    server.start()
    print("🔹 gRPC Image Service running on port 5014...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()