 # gRPC Image Service - Python (gRPC + MongoDB + GridFS)
 
 ## Description
 This microservice provides a gRPC server to manage image files associated with 3D models stored in MongoDB.  
 It exposes an RPC endpoint to delete images by model ID, removing both the GridFS stored binary file and the corresponding metadata document in MongoDB.  
 Designed for internal usage within a distributed system, it allows other services to coordinate image lifecycle actions via gRPC calls.
 
 ## Features
 - gRPC server with thread pool concurrency (max 10 workers)
 - Deletes image metadata document by `model_id` from MongoDB `images` collection
 - Deletes the actual image file stored in GridFS by referenced `image_id`
 - Uses environment variables for MongoDB connection configuration
 - Handles errors gracefully by returning success status and detailed messages in gRPC responses
 - Prints startup logs for visibility
 
 ## Endpoints (RPCs)
 | RPC                       | Description                                  |
 |---------------------------|----------------------------------------------|
 | `DeleteImageByModelId`    | Deletes the image and metadata associated with a specific model ID |
 
 ## Architecture: Simple Layered Design
 - **gRPC Layer**: Handles client connections and routes RPC calls to service implementation
 - **Service Layer**: Implements business logic for image deletion, querying MongoDB and GridFS
 - **Data Layer**: MongoDB client connection and GridFS bucket for managing files
 
 ## External Connections Diagram
 ```  
                   ┌─────────────┐
                   │ gRPC Client │
                   └──────┬──────┘
                          │ gRPC call
                          ▼
                   ┌───────────────┐
                   │ gRPC Server   │
                   │ (ImageService)│
                   └──────┬────────┘
                          │ MongoDB Driver
         ┌────────────────┴───────────────┐
         │                                │
   ┌─────────────┐                 ┌──────────────┐
   │  images     │                 │   GridFS     │
   │ collection  │                 │  file store  │
   └─────────────┘                 └──────────────┘
 ```  
 
 ## Environment Variables / Config
 - `MONGO_HOST`: MongoDB host (default: localhost)
 - `MONGO_PORT`: MongoDB port (default: 27017)
 - `MONGO_DB`: MongoDB database name (default: CatalogServiceDB)
 - `MONGO_USER`: MongoDB username
 - `MONGO_PASSWORD`: MongoDB password
 
 ## Running the Service
 ```bash
 # Install dependencies
 pip install grpcio grpcio-tools pymongo python-dotenv
 
 # Run the gRPC server
 python image_service_server.py
 ```  
 
 ## Recommendations & Notes
 - The server listens insecurely on `0.0.0.0:5014`; production use should add TLS encryption and authentication.
 - Proper error handling returns success flags and error messages in responses to aid client diagnostics.
 - MongoDB URI is dynamically constructed from env variables supporting different deployment environments.
 - Assumes `images` collection documents contain `model_id` and GridFS `image_id`; schema validation is not enforced.
 - No input validation for `model_id` is implemented; recommend adding validation to prevent injection or malformed queries.
 - Logging is minimal; consider adding structured and persistent logging for operations and errors.
 - No retries or fallback mechanisms on MongoDB/GridFS failures; such resilience can be added if needed.
 - Designed for synchronous RPC calls; if deletion is a costly operation, asynchronous or streaming patterns could be considered.
 - Suitable as a backend microservice component in a microservices architecture managing 3D model assets.
 
 ---