# Catalog Microservice - Flask (MongoDB + gRPC)

## Description
This microservice manages a catalog of 3D models. It allows authenticated users to delete their own uploaded models by name or ID. When a model is deleted by ID, the service also communicates with a separate image deletion microservice via gRPC to ensure consistency between model metadata and its associated image.
It follows separation of concerns and applies single-responsibility and modular design principles, aiming for maintainability and clarity.

## Features
- Model deletion by name or ID (only allowed by the creator)
- JWT-based user authentication for secure access
- MongoDB for flexible document-based data storage
- gRPC call to external image deletion service when deleting by ID
- Ownership validation before allowing deletion
- Environment-based configuration for MongoDB URI and JWT secret
- Clear error handling and debug output for traceability

## Endpoints

| Endpoint                          | Method | Description                                                                 |
|-----------------------------------|--------|-----------------------------------------------------------------------------|
| `/`                               | GET    | Health check – returns a welcome message                                   |
| `/models/<model_name>`           | DELETE | Deletes a model by name (only if current user is the creator)             |
| `/models/id/<model_id>`          | DELETE | Deletes a model by ID and also deletes associated image via gRPC service  |

## Architecture: SRP + Modular Layers

- **Presentation Layer**: Flask routes handle HTTP requests, JSON responses, and validation
- **Integration Layer**: gRPC stub communicates with `grpc-image-del-service` to coordinate image deletion
- **Data Access Layer**: MongoDB access using PyMongo, with collection-level operations
- Helpers abstract JWT decoding and model ownership validation for better reusability

## External Connections Diagram

```
              ┌──────────────┐
              │  Frontend    │
              └──────┬───────┘
                     │  REST (JSON)
                     ▼
              ┌──────────────┐
              │   Flask API  │
              └──────┬───────┘
                     │ PyMongo
                     ▼
              ┌──────────────┐
              │  MongoDB     │
              └──────────────┘
                     │
              gRPC call (internal)
                     ▼
              ┌──────────────────────┐
              │ Image Delete Service │
              └──────────────────────┘
```

## Environment Variables / Config

- `MONGO_URI`: MongoDB connection string for accessing `CatalogServiceDB`
- `SECRET_KEY`: Used to decode JWT tokens for authenticating users
- gRPC target channel: hardcoded as `grpc-image-del-service:5014` (can be moved to env var)
- `PORT`: Defaults to `5011` in `app.run`

## Running the Service

```bash
pip install -r requirements.txt
python app.py
# or with host and port:
python app.py --host 0.0.0.0 --port 5011
```

## Recommendations
- Move the gRPC service address to an environment variable for portability
- Implement JWT expiration verification in production for stronger security
- Use proper logging instead of `print` for production readiness
- Add a registration or upload endpoint to complete the catalog lifecycle
- Protect routes with proper auth decorators instead of manual token extraction
- Add unit and integration tests for routes and gRPC integration

---