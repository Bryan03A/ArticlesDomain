 # Catalog Customization Service - Sinatra (Ruby) + MongoDB + PostgreSQL (ActiveRecord)
 
 ## Description
 This microservice exposes endpoints for retrieving 3D catalog models from MongoDB and managing customized model entries stored in PostgreSQL.  
 It authenticates users by validating JWT Bearer tokens against an external authentication microservice.  
 Users can update their customized models’ parameters and pricing, with ownership enforced strictly by matching user IDs.  
 The service is implemented in Ruby using Sinatra for routing, MongoDB driver for catalog reads, and ActiveRecord ORM for PostgreSQL data management.  
 It delegates pricing calculation logic to a dedicated `PriceCalculator` module for clean separation of concerns.  
 
 ## Features
 - Retrieve full 3D model catalog from MongoDB (`GET /models`)
 - Update customized model parameters and recalculate final cost (`PUT /customize-model/:id`)
 - Token-based authentication by validating JWT tokens with external auth-service
 - Ownership enforcement: only the user who created a customized model can modify it
 - Dynamic table creation on startup for `customs` table if missing
 - Error handling with clear JSON responses and HTTP status codes
 
 ## Endpoints
 | Endpoint                 | Method | Description                                          |
 |--------------------------|--------|------------------------------------------------------|
 | `/models`                | GET    | Retrieves all 3D models from MongoDB catalog          |
 | `/customize-model/:id`   | PUT    | Updates customization params of a customized model by id (auth required) |
 
 ## Architecture: Simple N-Layer Design
 - **Presentation Layer**: Sinatra routes handle HTTP requests and responses, parse JSON, and manage control flow with error handling.
 - **Domain Layer**: ActiveRecord model `Custom` encapsulates customized model data and validations.
 - **Integration Layer**:  
    - MongoDB client for reading catalog data  
    - HTTP client to auth-service for token verification
 - **Utility Layer**: `PriceCalculator` module handles pricing business logic separate from route handlers
 
 ## External Communication Diagram
 ```  
                 ┌───────────────┐
                 │   Client App  │
                 └──────┬────────┘
                        │ HTTP REST JSON
                        ▼
                 ┌───────────────┐
                 │  Sinatra API  │
                 │ (Catalog +    │
                 │  Customization)│
                 └──────┬────────┘
                        │
 HTTP/REST Token Validation Request
                        ▼
                ┌─────────────────┐
                │  Auth-Service   │
                └─────────────────┘
                        ▲
     MongoDB Reads      │
     PostgreSQL CRUD    │
     Pricing Calculation│
                        │
                 ┌───────────────┐
                 │  MongoDB      │
                 └───────────────┘
                 ┌───────────────┐
                 │ PostgreSQL    │
                 └───────────────┘
 ```  
 
 ## Environment Variables / Configuration
 - `MONGO_URI`: MongoDB connection string (e.g. `mongodb+srv://user:pass@host/dbname`)
 - `POSTGRES_URI`: PostgreSQL connection string (e.g. `postgresql://user:pass@host:port/dbname`)
 - `PORT`: Service listen port (default `5013`)
 
 ## Running the Service
 ```bash
 # Install dependencies
 bundle install
 
 # Run Sinatra app binding to all interfaces on port 5013
 ruby app.rb -o 0.0.0.0 -p 5013
 ```  
 
 ## Recommendations & Notes
 - The service does not decode JWT tokens locally; it delegates validation to an external auth-service. This introduces network dependency and latency considerations.
 - The `customs` table is created at startup if missing but lacks migrations; consider managing schema changes with a proper migration tool (e.g., ActiveRecord migrations).
 - `custom_params` are stored as JSONB in PostgreSQL, updated via `.to_json` conversion to ensure proper format.
 - CORS is scaffolded with `rack-cors` but currently commented out; enable and configure for frontend integration as needed.
 - Logging is available via Ruby's Logger but not actively used; add logging for audit and debugging purposes.
 - Handle network errors or auth-service downtime gracefully to improve robustness.
 - Add unit and integration tests for authentication, data validation, and pricing logic to ensure reliability.
 - Consider rate limiting or other security measures to protect the auth endpoint and your service.
 
 ---