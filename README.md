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


