# Custom Delete Model Service - Sinatra (Ruby) with MongoDB & PostgreSQL Integration

 ## Description
 This microservice manages customized 3D models by integrating a MongoDB catalog of base models with a PostgreSQL relational store for customized instances. It offers secure deletion of customized models with token verification delegated to an external auth-service. Designed for modularity, it cleanly separates concerns between data access, authentication, and API routing.

 ## Features
 - Retrieve all base 3D catalog models stored in MongoDB
 - Securely delete customized models stored in PostgreSQL with ownership validation
 - Token verification through external auth-service ensuring centralized authentication
 - Automatic creation of PostgreSQL `customs` table with necessary schema on startup
 - Uses ActiveRecord ORM for relational data and native Mongo Ruby driver for document data
 - Graceful error handling with appropriate HTTP status codes and JSON error messages

 ## Endpoints

 | Endpoint               | Method | Description                                  |
 |------------------------|--------|----------------------------------------------|
 | `/models`              | GET    | Fetch all base 3D catalog models             |
 | `/customize-model/:id` | DELETE | Delete a customized model by ID (ownership enforced) |

 ## Architecture: Modular Layered Design

 - **Presentation Layer**: Sinatra routes process HTTP requests and responses
 - **Domain Layer**: Token verification and authorization logic abstracted in helper functions
 - **Data Access Layer**:  
    • MongoDB for base model storage  
    • PostgreSQL via ActiveRecord for customized model management

 ## External Connections Diagram

 ``` 
            ┌─────────────┐
            │  Frontend   │
            └─────┬───────┘
                  │ REST JSON
                  ▼
            ┌─────────────┐
            │  Sinatra API│
            └─────┬───────┘
                  │
         ┌────────┴────────┐
         │                 │
 ┌─────────────┐    ┌─────────────┐
 │  MongoDB    │    │ PostgreSQL  │
 └─────────────┘    └─────────────┘
 ```

 ## Environment Variables / Config

 - `MONGO_URI`: MongoDB connection string for catalog models
 - `POSTGRES_URI`: PostgreSQL connection string (with `?prepared_statements=false`)
 - `AUTH_SERVICE_URL`: URL for token verification service (e.g. `http://3.224.44.87/auth/profile`)
 - `PORT`: Service port (default 5012)

 ## Running the Service

 ```bash
 # Install dependencies (bundler, gems)
 bundle install
 # Run the Sinatra app
 ruby app.rb -o 0.0.0.0 -p 5012
 ```

 ## Recommendations
 - Enable and configure Rack CORS middleware for cross-origin access control
 - Use HTTPS between services to secure token transmission
 - Cache auth-service token validation results to improve performance
 - Add unit and integration tests for authorization and DB operations
 - Employ structured logging and monitoring for production readiness
 - Consider background cleanup jobs for orphaned customized models or data consistency checks