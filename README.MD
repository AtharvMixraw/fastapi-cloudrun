# FastAPI Cloud Run Todo App

A containerized FastAPI REST API deployed on Google Cloud Run with PostgreSQL database integration.

## Features
- CRUD operations for todos
- PostgreSQL database with Cloud SQL
- Secure credential management with Secret Manager
- Automatic scaling with Cloud Run

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Database**: PostgreSQL (Cloud SQL)
- **Deployment**: Google Cloud Run
- **Infrastructure**: Docker, Google Cloud Build

## API Endpoints
- `GET /` - Health check
- `GET /todos/` - List all todos
- `POST /todos/` - Create new todo
- `GET /todos/{id}` - Get specific todo
- `PUT /todos/{id}` - Update todo
- `DELETE /todos/{id}` - Delete todo

## Deployment
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/fastapi-cloudrun:latest
gcloud run deploy fastapi-service --image gcr.io/PROJECT_ID/fastapi-cloudrun:latest
```

## Live Demo
Visit the deployed API: [https://fastapi-service-870296606359.us-central1.run.app/docs](https://fastapi-service-870296606359.us-central1.run.app/docs)