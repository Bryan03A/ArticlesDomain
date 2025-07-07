 # Image Upload & Retrieval Service - Flask (MongoDB + GridFS)
 
 ## Description
 This microservice handles the storage, indexing, and retrieval of image files related to 3D models.  
 Images are uploaded via REST endpoints, saved as binary files using MongoDB's GridFS, and indexed in a separate `images` collection with metadata including the associated `model_id`.  
 Built using Flask, this service is intended to be part of a larger system where users manage 3D models and need to upload or visualize associated preview images.
 
 ## Features
 - Accepts image uploads via `multipart/form-data` and saves to GridFS
 - Associates each uploaded image with a `model_id`
 - Stores image metadata (`image_id`, `model_id`, `filename`) in a MongoDB collection
 - Retrieves metadata of all stored images via a REST endpoint
 - Returns actual image files as binary JPEGs using the `model_id`
 - Environment-based MongoDB configuration via `.env` file
 - Includes robust error handling for file I/O and DB exceptions
 
 ## Endpoints
 
 | Endpoint                   | Method | Description                                            |
 |----------------------------|--------|--------------------------------------------------------|
 | `/upload`                 | POST   | Uploads an image and links it to a `model_id`          |
 | `/images`                 | GET    | Returns metadata of all stored images                 |
 | `/image/<model_id>`       | GET    | Returns the binary image file associated with a model |
 
 ## Architecture: 3-Layer Design
 
 - **Presentation Layer**: Flask routes handle HTTP logic and request parsing
 - **Integration Layer**: MongoDB GridFS for image binary storage and metadata document handling
 - **Storage Layer**: GridFS bucket for file chunks and `images` collection for document mapping
 
 ## External Connections Diagram
 ```text
                   ┌──────────────┐
                   │  Frontend    │
                    └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │    Flask     │
                   │   (API)      │
                   └──────┬───────┘
                          │
         ┌────────────────┴───────────────┐
         │                                │
   ┌─────────────┐                 ┌──────────────┐
   │  images     │                 │   GridFS     │
   │ collection  │                 │  binary store│
   └─────────────┘                 └──────────────┘
 ```
 
 ## Environment Variables / Config
 
 - `MONGO_HOST`: MongoDB host (default `localhost`)
 - `MONGO_PORT`: MongoDB port (default `27017`)
 - `MONGO_DB`: Target database name (default `CatalogServiceDB`)
 - `MONGO_USER`: MongoDB username
 - `MONGO_PASSWORD`: MongoDB password
 
 ## Running the Service
 
 ```bash
 pip install -r requirements.txt
 python image_service_flask.py
 ```
 
 ## Recommendations
 - Enable and configure CORS properly for cross-domain frontend access (currently commented)
 - Add authentication (e.g., JWT or API keys) for upload and read operations
 - Implement file type validation to restrict uploads to allowed MIME types (e.g., only images)
 - Support pagination and filtering on the `/images` endpoint
 - Store additional metadata like upload timestamp, uploader ID, or image type
 - Add logging (e.g., with `logging` module or Sentry) for operational observability
 - Use content hashing or UUIDs to avoid duplicate image uploads or filename collisions
 - Store MIME type with image metadata and return proper `Content-Type` on retrieval
 - Add rate limiting or quotas for production use
 
 ---
