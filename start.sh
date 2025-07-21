#!/bin/bash

# Get port from environment variable or use default
PORT=${PORT:-8000}

# Run the application binding to all interfaces (0.0.0.0)
uvicorn main:app --host 0.0.0.0 --port $PORT