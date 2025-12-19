#!/bin/sh
set -e

# Use the PORT environment variable provided by Railway, default to 8080 if not set
PORT="${PORT:-8080}"

echo "Starting Uvicorn on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
