# Custom Model Service - Sinatra (Ruby) + MongoDB + PostgreSQL  
  
 ## Description  
 This microservice manages customized 3D models created by users. It integrates MongoDB to store the base catalog of models and PostgreSQL to store user customizations, pricing details, and state. The service performs user authentication and authorization by verifying JWT tokens with an external auth-service. Upon customization, it calculates final prices and creates corresponding orders in an external order-status-service. State changes (e.g., marking a model as paid) are securely handled with role-based permissions.  
  
 ## Features  
 - Retrieve base 3D catalog models from MongoDB  
 - Create customized models with user parameters and price calculation  
 - Store customized models in PostgreSQL with metadata including state and costs  
 - Secure JWT-based authentication and authorization delegated to external auth-service  
 - Create orders in order-status-service after customization creation  
 - Retrieve customized models per user with access control  
 - Update customized model states (e.g., to `paid`) with permission checks  
 - Automatic creation of required database schema (tables and columns) on startup  
  
 ## Endpoints  
  
 | Endpoint                     | Method | Description                                                        |  
 |------------------------------|--------|--------------------------------------------------------------------|  
 | `/models`                    | GET    | Retrieve all base 3D catalog models                                |  
 | `/customize-model`           | POST   | Create a customized model, calculate final price, and create order|  
 | `/customize-models`          | GET    | List all customized models for the authenticated user             |  
 | `/customize-model/:id`       | GET    | Retrieve a customized model by ID with access control             |  
 | `/customize-model/:id/state` | PUT    | Update the state of a customized model (e.g., mark as `paid`)     |  
  
 ## Architecture: Layered + External Auth + Microservice Integration  
  
 - **Presentation Layer**:  
   - Sinatra routes handle HTTP requests and responses, parse JSON, and return JSON.  
  
 - **Domain Layer**:  
   - Business logic for price calculation delegated to `PriceCalculator` class.  
   - Token verification and user authorization logic implemented with HTTP calls to external auth-service.  
   - State management and permission enforcement for customized models.  
  
 - **Data Access Layer**:  
   - Mongo Ruby driver accesses `models` collection in MongoDB for base catalog data.  
   - ActiveRecord manages `customs` table in PostgreSQL for customized model storage.  
   - Raw SQL ensures table and schema readiness on service startup.  
  
 ## External Connections Diagram  
  
 ```  
                ┌──────────────┐               ┌───────────────┐  
                │   Frontend   │               │ Auth-Service  │  
                │   Client     │               │ (JWT Verify)  │  
                └──────┬───────┘               └──────┬────────┘  
                       │ REST JSON                      │ REST JSON  
                       ▼                               ▼  
                ┌──────────────┐               ┌────────────────┐  
                │   Sinatra    │──────────────▶│ Order-Status   │  
                │   (API)      │    HTTP POST │ (Create orders) │  
                └──────┬───────┘               └────────────────┘  
                       │  
         ┌─────────────┼─────────────┐  
         │             │             │  
         ▼             ▼             ▼  
    ┌─────────┐   ┌─────────────┐   ┌───────────────┐  
    │ MongoDB │   │ PostgreSQL  │   │ PriceCalculator│  
    │ models  │   │ customs     │   │ (Business logic)│  
    └─────────┘   └─────────────┘   └───────────────┘  
 ```  
  
 ## Environment Variables / Config  
  
 - `MONGO_URI`: MongoDB connection string for catalog models  
 - `POSTGRES_URI`: PostgreSQL connection string for customized models  
 - `PORT`: Service port (default `5007`)  
  
 ## Running the Service  
  
 ```bash  
 bundle install  
 ruby service.rb  
 ```  
  
 ## Recommendations  
 - Enable and configure Rack CORS middleware for controlled cross-origin access  
 - Use a secrets manager or environment variable vault for sensitive config values  
 - Add structured logging and monitoring to track user actions and errors  
 - Implement retries and error handling for external HTTP calls (auth-service, order-status-service)  
 - Write unit tests for price calculation, token verification, and authorization logic  
 - Write integration tests covering endpoint security and database interactions  
  
 ---  