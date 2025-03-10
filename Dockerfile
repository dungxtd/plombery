
# Stage 1: Build frontend assets
FROM node:20-slim as frontend-builder
WORKDIR /app/frontend

# Copy frontend files
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install --frozen-lockfile

COPY frontend/ ./
RUN yarn build

# Stage 2: Python application
FROM python:3.11-alpine

WORKDIR /app

# Install build dependencies, install Python packages, then remove build dependencies
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    && pip install --no-cache-dir uvicorn[standard] \
    && apk del .build-deps

# Copy Python package files and install dependencies
COPY src/ ./src/
COPY pyproject.toml setup.cfg ./

COPY examples/ ./examples/
RUN cd examples \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache

# Copy built frontend assets
COPY --from=frontend-builder /app/src/plombery/static/ ./src/plombery/static/

# Set environment variables
ENV PORT=8000

# Expose the application port
EXPOSE 8000

# Run the application
CMD ["sh", "-c", "cd examples && ./run.sh"]
