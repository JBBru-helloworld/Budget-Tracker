#!/bin/bash

# Create necessary directories
mkdir -p /opt/render/project/src/backend/uploads
mkdir -p /opt/render/project/src/backend/static/avatars

# Set permissions
chmod 755 /opt/render/project/src/backend/uploads
chmod 755 /opt/render/project/src/backend/static

# Start the application
cd /opt/render/project/src/backend
uvicorn app.main:app --host 0.0.0.0 --port $PORT