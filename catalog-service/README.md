# Catalog Microservice - Flask (MongoDB + JWT + gRPC integration)

## Description
This microservice manages a catalog of 3D models, providing full CRUD capabilities with strict ownership validation enforced via JWT authentication. Users can create, retrieve, update, and delete models. Deletion by ID triggers a coordinated call to an external image deletion microservice over gRPC, ensuring consistency between metadata and stored images. The service is designed for maintainability, clarity, and secure access, following modular principles and a clean separation of concerns.

## Features
- Create 3D models with metadata including creator info extracted from JWT tokens
- Retrieve models by various filters: all models, by creator, by name, or by ID
- Update model data with ownership validation
- Delete models with ownership checks and cascade image deletion via gRPC
- JWT authentication and token decoding with error handling
- MongoDB document storage via PyMongo
- Optional CORS support configured for multiple trusted origins
- Debug logging for token and ownership validation to ease troubleshooting

## Endpoints

| Endpoint                      | Method | Description                                           |
|-------------------------------|--------|-------------------------------------------------------|
| `/`                           | GET    | Health check and welcome message                      |
| `/models`                     | POST   | Create a new 3D model (requires valid JWT)           |
| `/models`                     | GET    | Retrieve all models                                   |
| `/models/user/<user_id>`      | GET    | Retrieve models created by a specific user           |
| `/models/<model_name>`        | GET    | Retrieve a single model by name                        |
| `/models/id/<model_id>`       | GET    | Retrieve a single model by MongoDB ObjectId           |
| `/models/<model_name>`        | PUT    | Update model by name (owner only)                      |
| `/models/id/<model_id>`       | PUT    | Update model by ID (owner only)                        |

## Architecture: Modular N-Layer Design

- **Presentation Layer**: Flask HTTP routes handle requests, responses, and input validation
- **Domain Layer**: Authentication, authorization, and ownership validation logic encapsulated in helpers
- **Data Access Layer**: MongoDB interaction abstracted through PyMongo collection operations

## External Connections Diagram

```
               ┌──────────────┐
               │   Frontend   │
               └──────┬───────┘
                      │ REST JSON
                      ▼
               ┌──────────────┐
               │   Flask API  │
               └──────┬───────┘
                      │ PyMongo
                      ▼
               ┌──────────────┐
               │   MongoDB    │
               └──────────────┘
```

## Environment Variables / Config

- `MONGO_URI`: MongoDB connection URI for the `CatalogServiceDB` database
- `SECRET_KEY`: JWT secret key for decoding tokens
- `PORT`: Service port (default 5003)
- CORS origins configured but commented out (adjust as needed)

## Running the Service

```bash
pip install -r requirements.txt
python app.py
# or to specify host and port
python app.py --host 0.0.0.0 --port 5003
```

## Recommendations
- Enable JWT expiration (`verify_exp`) in production for security
- Configure CORS for allowed client origins
- Replace print debugging with structured logging
- Add endpoint to upload/register models to complete the full catalog lifecycle
- Secure environment variables with secrets manager or vault
- Write comprehensive unit and integration tests covering authentication, authorization, and data operations
- Consider refactoring ownership checks into decorators for cleaner route code