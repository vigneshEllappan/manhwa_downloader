#!/bin/bash

# Check if we are in development mode (you can set this via environment variable)
if [ "$FLASK_ENV" = "development" ]; then
    # In development mode, use Flask's built-in server
    echo "Running in Development Mode..."
    python backend/app.py
else
    # In production mode, use gunicorn
    echo "Running in Production Mode..."
    gunicorn --chdir backend app:app -b 0.0.0.0:8080
fi
