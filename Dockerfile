# Stage 1: Build Frontend
FROM node:20-alpine as frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Runtime
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Copy built frontend from Stage 1
# We ensure the target directory exists
RUN mkdir -p /app/frontend/dist
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

# Expose port
ENV PORT=8080
EXPOSE 8080

# Run
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
