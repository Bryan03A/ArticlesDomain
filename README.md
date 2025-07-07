## 8️⃣ **Catalog delete Service** (Python / Flask + MongoDB + gRPC)

- **🧠 Purpose**:  
  Manages 3D model metadata stored in MongoDB. Allows only the **creator** of a model to delete it. When deleted by ID, it coordinates with a gRPC service to also remove the associated image.

- **🧪 Port**: `5011`

- **🧰 Tech Stack**:
  - **Language**: Python  
  - **Framework**: Flask  
  - **Database Driver**: PyMongo  
  - **RPC**: gRPC (`protobuf` + `grpcio`)  
  - **Auth**: JWT with PyJWT  
  - **Config**: `python-dotenv` for environment variable management

- **🛢️ Database**:
  - **Type**: NoSQL  
  - **Engine**: MongoDB Atlas  
  - **Collection**: `models` — stores 3D model documents (`_id`, `name`, `created_by`, etc.)

- **🔐 Security**:
  - Uses Bearer token from the `Authorization` header
  - Decodes token using `SECRET_KEY` (from `.env`)
  - Only the **creator** (`username` in token) can delete a model (`created_by` in DB)
  - Token expiration (`exp`) verification is disabled — enable for production

- **📡 Communication**:
  - **REST (JSON)**: public-facing endpoints  
  - **gRPC (internal)**: connects to `grpc-image-del-service:5014`  
    - Calls `DeleteImageByModelId(model_id)` to delete associated image on model deletion

- **🌍 Endpoints**:
  - `GET /` — Health check / welcome message  
  - `DELETE /models/<model_name>` — Deletes a model by its name (owner only)  
  - `DELETE /models/id/<model_id>` — Deletes by ID and triggers image deletion via gRPC

- **🎨 Design Patterns**:
  - **Single Responsibility Principle**: Helpers are used to isolate JWT decoding and ownership validation  
  - **Dependency Inversion (basic)**: gRPC stub is abstracted through a configured channel

- **🏗️ Architecture**: Light N-layered structure
  - **Presentation Layer**: Flask routes + optional CORS  
  - **Integration Layer**: gRPC client for image operations  
  - **Data Access Layer**: Direct DB access via `models_collection`

- **🛠️ Notes**:
  - Token decoding and ownership checks are printed to console for debugging  
  - CORS setup exists but is commented out — configure properly in production  
  - Error handling is consistent using JSON responses and appropriate HTTP status codes

---

## 8️⃣ **Catalog Service** (Python / Flask + MongoDB)

- **🧠 Purpose**:  
  Manages a catalog of 3D models including creation, retrieval, update, and deletion. Enforces ownership rules so only the creator of a model can update or delete it. Supports querying models by ID, name, or creator. Uses JWT for authentication and MongoDB for flexible document storage.

- **🧪 Port**: `5003`

- **🧰 Tech Stack**:  
  - Language: Python  
  - Framework: Flask  
  - Database: MongoDB (via PyMongo)  
  - Auth: JWT (PyJWT)  
  - Config: python-dotenv for environment variables  
  - Optional CORS support (commented)

- **🛢️ Database**:  
  - Type: NoSQL document store  
  - Engine: MongoDB Atlas  
  - Collection: `models` (stores 3D model metadata with fields like `_id`, `name`, `created_by`, etc.)

- **🔐 Security**:  
  - JWT token extracted from Authorization header (Bearer token)  
  - Token decoded with secret key, no expiration check (should be enabled in production)  
  - Ownership validation: only user matching `created_by` can update or delete the model  
  - Returns 401 if token is missing or invalid, 403 for unauthorized access

- **📡 Communication**: REST (JSON)  
  - Standard CRUD endpoints for models  
  - Clear JSON error responses with appropriate HTTP status codes

- **🌍 Endpoints**:

  | Endpoint                   | Method | Description                                   |
  |----------------------------|--------|-----------------------------------------------|
  | `/`                        | GET    | Health check, welcome message                 |
  | `/models`                  | POST   | Create a new model (requires valid JWT)      |
  | `/models`                  | GET    | Retrieve all models                           |
  | `/models/user/<user_id>`   | GET    | Retrieve all models created by specified user|
  | `/models/<model_name>`     | GET    | Retrieve model by name                         |
  | `/models/id/<model_id>`    | GET    | Retrieve model by MongoDB ObjectId            |
  | `/models/<model_name>`     | PUT    | Update model by name (owner only)             |
  | `/models/id/<model_id>`    | PUT    | Update model by ID (owner only)                |

- **🎨 Design Pattern**:  
  - Single Responsibility: helpers isolate JWT decoding and ownership checking  
  - Consistent error handling and response formatting  
  - Separation of concerns: route handlers focus on HTTP layer, business rules enforced by token and DB checks

- **🏗️ Architecture**: 3-layer (N-layer) architecture  
  - Presentation Layer: Flask route handlers  
  - Domain Layer: Authorization logic & ownership validation helpers  
  - Data Access Layer: MongoDB collection operations via PyMongo

- **🛠️ Notes**:  
  - ObjectIds are converted to strings before JSON serialization  
  - JWT expiration check is disabled (for dev/testing) — should be enabled in prod  
  - CORS middleware is prepared but commented out, configure as needed  
  - Debug print statements present for token decoding and ownership verification  
  - Error handling returns JSON with error messages and HTTP status codes  
  - MongoDB connectivity checked at startup with ping command  
  - Designed for maintainability and clear traceability of ownership and permissions

---

## 9️⃣ **Custom Model Delete Service** (Ruby / Sinatra + MongoDB + PostgreSQL)

- **🧠 Purpose**:  
  Manages customized 3D models created by users, allowing retrieval of catalog models and secure deletion of customized models with authorization checks via an external auth-service. Combines document storage for base models with relational storage for customizations and their costs.

- **🧪 Port**: `5012`

- **🧰 Tech Stack**:  
  - Language: Ruby  
  - Framework: Sinatra  
  - Databases: MongoDB (for catalog models), PostgreSQL (for customized models)  
  - ORM: ActiveRecord for PostgreSQL  
  - Auth: JWT token verification delegated to external auth-service via HTTP call  
  - Middleware: Rack CORS (commented, configurable)  

- **🛢️ Database**:  
  - MongoDB stores base 3D models in `models` collection  
  - PostgreSQL stores customized models in `customs` table with fields like `model_id`, `user_id`, `created_by`, `custom_params` (JSONB), `cost_initial`, `cost_final`, and timestamps  
  - `customs` table auto-created if not existing  

- **🔐 Security**:  
  - Token passed in Authorization header is verified by an external `auth-service` endpoint (`/auth/profile`)  
  - Only the user who created a custom model (`user_id`) can delete it  
  - Proper HTTP error responses with status codes and JSON messages on invalid token, unauthorized access, or missing model  

- **📡 Communication**: REST (JSON)  
  - GET `/models` returns all base catalog models from MongoDB  
  - DELETE `/customize-model/:id` deletes a customized model after validating JWT token and ownership  

- **🌍 Endpoints**:

  | Endpoint               | Method | Description                                  |
  |------------------------|--------|----------------------------------------------|
  | `/models`              | GET    | Retrieve all base 3D catalog models          |
  | `/customize-model/:id` | DELETE | Delete customized model by ID (authorized users only) |

- **🎨 Design Pattern**:  
  - Separation of concerns with ActiveRecord handling PostgreSQL and Mongo Ruby driver for MongoDB  
  - Token verification delegated to an external service for single source of truth on authentication  
  - Error handling centralized in endpoint with proper status codes  

- **🏗️ Architecture**:  
  - Presentation Layer: Sinatra routes handling HTTP requests  
  - Domain Layer: Token verification and authorization logic in helper method  
  - Data Access Layer: MongoDB driver for catalog models and ActiveRecord for customized models  

- **🛠️ Notes**:  
  - Rack CORS middleware setup commented out but ready for use  
  - Uses raw SQL to ensure `customs` table creation if absent  
  - Deletes customized models only if ownership verified  
  - Handles exceptions gracefully returning JSON error messages  
  - Runs on port 5012, binds to all interfaces  
  - Designed for maintainability and clear separation between catalog base models and customized instances

---

---

## 9️⃣ **Custom Model Delete Service** (Ruby / Sinatra + MongoDB + PostgreSQL)

- **🧠 Purpose**:  
  Manages customized 3D models created by users, allowing retrieval of catalog models and secure deletion of customized models with authorization checks via an external auth-service. Combines document storage for base models with relational storage for customizations and their costs.

- **🧪 Port**: `5012`

- **🧰 Tech Stack**:  
  - Language: Ruby  
  - Framework: Sinatra  
  - Databases: MongoDB (for catalog models), PostgreSQL (for customized models)  
  - ORM: ActiveRecord for PostgreSQL  
  - Auth: JWT token verification delegated to external auth-service via HTTP call  
  - Middleware: Rack CORS (commented, configurable)  

- **🛢️ Database**:  
  - MongoDB stores base 3D models in `models` collection  
  - PostgreSQL stores customized models in `customs` table with fields like `model_id`, `user_id`, `created_by`, `custom_params` (JSONB), `cost_initial`, `cost_final`, and timestamps  
  - `customs` table auto-created if not existing  

- **🔐 Security**:  
  - Token passed in Authorization header is verified by an external `auth-service` endpoint (`/auth/profile`)  
  - Only the user who created a custom model (`user_id`) can delete it  
  - Proper HTTP error responses with status codes and JSON messages on invalid token, unauthorized access, or missing model  

- **📡 Communication**: REST (JSON)  
  - GET `/models` returns all base catalog models from MongoDB  
  - DELETE `/customize-model/:id` deletes a customized model after validating JWT token and ownership  

- **🌍 Endpoints**:

  | Endpoint               | Method | Description                                  |
  |------------------------|--------|----------------------------------------------|
  | `/models`              | GET    | Retrieve all base 3D catalog models          |
  | `/customize-model/:id` | DELETE | Delete customized model by ID (authorized users only) |

- **🎨 Design Pattern**:  
  - Separation of concerns with ActiveRecord handling PostgreSQL and Mongo Ruby driver for MongoDB  
  - Token verification delegated to an external service for single source of truth on authentication  
  - Error handling centralized in endpoint with proper status codes  

- **🏗️ Architecture**:  
  - Presentation Layer: Sinatra routes handling HTTP requests  
  - Domain Layer: Token verification and authorization logic in helper method  
  - Data Access Layer: MongoDB driver for catalog models and ActiveRecord for customized models  

- **🛠️ Notes**:  
  - Rack CORS middleware setup commented out but ready for use  
  - Uses raw SQL to ensure `customs` table creation if absent  
  - Deletes customized models only if ownership verified  
  - Handles exceptions gracefully returning JSON error messages  
  - Runs on port 5012, binds to all interfaces  
  - Designed for maintainability and clear separation between catalog base models and customized instances

---
## 8️⃣ **Catalog Customization Update Service** (Ruby / Sinatra + MongoDB + PostgreSQL + ActiveRecord)

- **🧠 Purpose**:  
  Provides endpoints to fetch 3D model catalog data from MongoDB and to create/update customized model entries stored in PostgreSQL. It verifies user authentication via an external auth-service using JWT Bearer tokens, enforces ownership for customization edits, and recalculates pricing based on customization parameters.

- **🧪 Port**: `5013`

- **🧰 Tech Stack**:
  - **Language**: Ruby  
  - **Framework**: Sinatra  
  - **Database Drivers**:  
    - MongoDB Ruby Driver (`mongo` gem) for catalog models  
    - ActiveRecord for PostgreSQL access and ORM  
  - **Authentication**: JWT tokens validated via HTTP call to external auth-service  
  - **Utilities**:  
    - `dotenv` for environment variable loading  
    - `rack-cors` commented but ready for CORS support  
    - `logger` available but not explicitly used  
  - **Custom Logic**: `price_calculator.rb` (external module) for recalculating customized model pricing

- **🛢️ Database**:
  - **MongoDB**:  
    - **URI** from env var `MONGO_URI`  
    - **Collection**: `models` — stores 3D model metadata documents  
  - **PostgreSQL**:  
    - **URI** from env var `POSTGRES_URI`  
    - **Table**: `customs` — stores customized models with fields:  
      - `id`: SERIAL PK  
      - `model_id` (text)  
      - `user_id` (text)  
      - `created_by` (text)  
      - `custom_params` (JSONB)  
      - `cost_initial` (decimal)  
      - `cost_final` (decimal)  
      - `created_at` (timestamp)

- **🔐 Security**:
  - Expects Bearer JWT token in `Authorization` header  
  - Token is verified by making an HTTP GET request to auth-service `/auth/profile` endpoint  
  - Valid token returns user details (`username`, `email`, `user_id`)  
  - Customization updates only allowed if the `user_id` matches the `user_id` of the stored customized model  
  - Errors raise exceptions caught with 400 status and JSON error message

- **📡 Communication**:
  - **REST (JSON)**:  
    - `GET /models` — returns all catalog models from MongoDB  
    - `PUT /customize-model/:id` — updates customization of a model by ID  
  - **External Auth-Service**: HTTP REST call to validate tokens and get user profile info

- **🌍 Endpoints**:
  - `GET /models`  
    - Fetch all models from MongoDB and return as JSON array  
  - `PUT /customize-model/:id`  
    - Authenticates user token  
    - Finds customized model by `id` in PostgreSQL  
    - Validates ownership (`user_id`)  
    - Parses incoming JSON body with new `custom_params`  
    - Calls `PriceCalculator.calculate(initial_cost, custom_params)` to update `cost_final`  
    - Saves updated customization and returns success message with updated model JSON  

- **🎨 Design Patterns**:
  - **ActiveRecord** ORM abstracts PostgreSQL model and validations  
  - **Separation of concerns**: price calculation delegated to `PriceCalculator` module  
  - **Exception handling** wraps endpoint logic to return proper HTTP error codes and messages  
  - **Externalized authentication**: token validation delegated to auth microservice

- **🏗️ Architecture**:
  - **Presentation Layer**: Sinatra routes  
  - **Domain Layer**: ActiveRecord `Custom` model representing customized catalog entries  
  - **Integration Layer**:  
    - MongoDB client for catalog reads  
    - HTTP client for auth-service token verification  
  - **Utilities**: price calculator module for business logic

- **🛠️ Notes**:
  - The table `customs` is created if missing on startup (schema migration is manual)  
  - `custom_params` are stored as JSONB in PostgreSQL, updated with `.to_json` conversion  
  - No explicit CORS enabled, but scaffolded with `rack-cors` commented out  
  - The server binds on all interfaces (`0.0.0.0`) and port `5013`  
  - Error messages are descriptive, returned in JSON with HTTP 400 status on failure  
  - Token verification relies on an external service, so network latency or failure can impact response times  
  - No direct JWT decoding is done locally; token is verified via remote API  
  - Code could benefit from logging and more granular error handling for production readiness

---

# 9️⃣ **gRPC Image Service** (Python + gRPC + MongoDB + GridFS)

- **🧠 Purpose**:  
  Implements a gRPC server that manages image deletion related to 3D models stored in MongoDB.  
  Specifically, it allows deleting an image by model ID by removing the corresponding file from GridFS and the image metadata document from MongoDB.  
  Designed to serve as an internal microservice for image lifecycle management in a distributed system.

- **🧪 Port**: `5014`

- **🧰 Tech Stack**:
  - **Language**: Python  
  - **gRPC Framework**: `grpcio` with auto-generated `image_service_pb2` and `image_service_pb2_grpc`  
  - **MongoDB Driver**: `pymongo` and `gridfs` for storing and deleting image files  
  - **Configuration**: `python-dotenv` for environment variables

- **🛢️ Database**:
  - **Type**: NoSQL  
  - **Engine**: MongoDB  
  - **Collections**:  
    - `images` — stores image metadata documents with at least `model_id` and `image_id` fields  
    - **GridFS** bucket — stores the actual image binary files referenced by `image_id`

- **🔐 Security**:
  - No explicit authentication or encryption configured in this code (insecure gRPC port used)  
  - Assumes internal trusted network access or to be secured externally

- **📡 Communication**:
  - **gRPC service** exposing `DeleteImageByModelId` RPC method  
  - Client sends `DeleteImageRequest` with a `model_id`  
  - Server queries MongoDB for image metadata by `model_id`, deletes the GridFS file by `image_id`, then deletes the metadata document  
  - Returns `DeleteImageResponse` with success status and message

- **🌍 Endpoints / RPCs**:
  - `DeleteImageByModelId(DeleteImageRequest) -> DeleteImageResponse`  
    - Deletes image file and metadata linked to given `model_id`  
    - Responds with success or failure message  

- **🎨 Design Patterns**:
  - **gRPC Server Stub** implemented by subclassing generated `ImageServiceServicer`  
  - Exception handling inside RPC method to capture and return error messages cleanly  
  - Uses MongoDB `GridFS` API for binary file deletion  
  - Environment-driven configuration for DB connection

- **🏗️ Architecture**:
  - **gRPC Layer**: Server setup with a thread pool executor for concurrency  
  - **Data Layer**: MongoDB connection + GridFS bucket for file operations  
  - **Service Layer**: Implements business logic for deletion by `model_id`  

- **🛠️ Notes**:
  - MongoDB URI is constructed dynamically using credentials and host/port from environment variables  
  - gRPC server listens insecurely on all interfaces, port `5014` — consider TLS for production  
  - Error handling returns detailed error messages in the gRPC response, aiding debugging  
  - No retry or resilience logic present; a single deletion failure is returned immediately  
  - Logs a startup message to the console; could be improved with structured logging  
  - Assumes `images` collection documents contain `model_id` and `image_id` fields consistent with GridFS references  
  - No input validation on `model_id` format — could be enhanced for security and robustness  
  - Designed for internal use, typically called by other microservices managing model lifecycle

---

# 🔟 **Image Upload & Retrieval Service** (Python + Flask + MongoDB + GridFS)

- **🧠 Purpose**:  
  A RESTful microservice that enables uploading, storing, and retrieving 3D model images using MongoDB and GridFS.  
  This service accepts image uploads (e.g. JPG), stores binary data in GridFS, and maintains a metadata reference in the `images` collection.  
  It provides endpoints to upload images, retrieve them by model ID, and list all stored image metadata.  

- **🧪 Port**: `5009`

- **🧰 Tech Stack**:
  - **Language**: Python  
  - **Framework**: Flask  
  - **Database Driver**: `pymongo` for MongoDB and `gridfs` for file storage  
  - **CORS**: Optional, scaffolded with `flask-cors` (currently commented out)  
  - **Environment Loader**: `python-dotenv`  

- **🛢️ Database**:
  - **Type**: NoSQL  
  - **Engine**: MongoDB  
  - **Collections**:  
    - `images` — stores metadata documents for uploaded images (e.g., `name`, `model_id`, `image_id`)  
    - **GridFS** — stores actual binary image files, referenced by `image_id`

- **🔐 Security**:
  - No authentication or authorization is implemented — assumes internal use or development stage  
  - CORS is scaffolded but currently disabled (commented line with allowed frontend origin)  
  - File validation (e.g., MIME type check) is minimal — only checks existence of keys  

- **📡 Communication**:
  - **REST Endpoints (JSON / Binary)**:
    - `POST /upload` — Uploads an image tied to a `model_id`  
    - `GET /images` — Retrieves metadata for all stored images  
    - `GET /image/<model_id>` — Fetches a single image file by its associated model ID  

- **🌍 Endpoints**:
  - `POST /upload`  
    - Requires `image` in form-data  
    - Requires `model_id` as form parameter  
    - Saves binary file to GridFS  
    - Inserts metadata (`name`, `image_id`, `model_id`) to `images` collection  
    - Returns image ID and success message  
  - `GET /images`  
    - Lists all image metadata in the `images` collection (excluding `_id`)  
  - `GET /image/<model_id>`  
    - Looks up image metadata by `model_id`  
    - Retrieves binary data from GridFS using `image_id`  
    - Returns binary JPEG image via Flask’s `send_file`  

- **🎨 Design Patterns**:
  - **Separation of Concerns**:  
    - GridFS handles file storage  
    - MongoDB collection handles metadata  
    - Flask manages HTTP interactions  
  - **Exception Handling**:
    - Errors (e.g., missing fields, file not found, DB exceptions) are caught and returned as JSON with proper HTTP codes  

- **🏗️ Architecture**:
  - **Presentation Layer**: Flask routes and response formatting  
  - **Integration Layer**: MongoDB connection with GridFS for binary files  
  - **Storage Layer**:  
    - GridFS for image binaries  
    - `images` collection for metadata (mapping model ID to file ID)

- **🛠️ Notes**:
  - MongoDB connection is built dynamically using credentials and DB info from environment variables  
  - The server runs on `0.0.0.0:5009`, exposing it on all interfaces — restrict in production  
  - CORS is prepared but disabled; configure properly if frontend access is needed  
  - `image_id` is stored as a string in MongoDB metadata for easier querying  
  - File type is not validated — recommend checking file MIME types or extensions before saving  
  - Retrieval endpoint returns raw JPEG — only `.jpg` assumed; consider validating content-type dynamically  
  - Environment-sensitive and lightweight — easily containerized or extended for production with auth, logging, etc.  
  - Could benefit from UUID-based image naming and duplicate prevention for production use  

---
