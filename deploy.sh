#!/bin/bash

# FastAPI Cloud Run Deployment Script

set -e  # Exit on any error

echo " Starting FastAPI deployment to Google Cloud Run..."

# Configuration
PROJECT_ID=atharvmishra-2022bcs0115
REGION=us-central1
INSTANCE_CONNECTION_NAME=atharvmishra-2022bcs0115:us-central1:fastapi-mysql
DB_PASSWORD=""  

echo " Configuration:"
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Instance: $INSTANCE_CONNECTION_NAME"
echo ""

# Set gcloud config
echo "Setting gcloud configuration..."
gcloud config set project ${PROJECT_ID}
gcloud config set run/region ${REGION}

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com

# Create service account
echo " Creating service account..."
gcloud iam service-accounts create cloudrun-cloudsql-sa \
  --display-name "cloudrun-cloudsql-sa" || echo "   Service account might already exist"

SA_EMAIL=cloudrun-cloudsql-sa@${PROJECT_ID}.iam.gserviceaccount.com

# Grant permissions
echo " Granting permissions to service account..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

# Store password in Secret Manager
echo " Storing database password in Secret Manager..."
echo -n "${DB_PASSWORD}" | gcloud secrets create db-password \
  --data-file=- \
  --replication-policy="automatic" || echo "   Secret might already exist"

# Build and push container
echo " Building and pushing container to Google Container Registry..."
gcloud builds submit --tag gcr.io/${PROJECT_ID}/fastapi-cloudrun:latest .

# Deploy to Cloud Run
echo " Deploying to Cloud Run..."
gcloud run deploy fastapi-service \
  --image gcr.io/${PROJECT_ID}/fastapi-cloudrun:latest \
  --platform managed \
  --region ${REGION} \
  --add-cloudsql-instances ${INSTANCE_CONNECTION_NAME} \
  --service-account ${SA_EMAIL} \
  --set-env-vars INSTANCE_CONNECTION_NAME=${INSTANCE_CONNECTION_NAME},DB_USER=postgres,DB_NAME=fastapi_db \
  --set-secrets DB_PASS=db-password:latest \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi

# Get service URL
echo " Getting service URL..."
SERVICE_URL=$(gcloud run services describe fastapi-service --region=${REGION} --format="value(status.url)")

echo ""
echo " Deployment completed successfully!"
echo " Your FastAPI service is live at: $SERVICE_URL"
echo ""
echo " Test your service with these commands:"
echo "   curl $SERVICE_URL/"
echo "   curl -X POST $SERVICE_URL/todos/ -H 'Content-Type: application/json' -d '{\"title\":\"Hello Cloud Run\",\"description\":\"My first todo!\"}'"
echo "   curl $SERVICE_URL/todos/"
echo ""
echo " View logs with: gcloud run services logs read fastapi-service --region=${REGION}"
echo " Don't forget to add this to your resume!"