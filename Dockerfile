
# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
# Install hatch to build the project/install deps
RUN pip install --no-cache-dir hatch

# Generate constraints or requirements if needed, but for simplicity we'll just install directly in final stage or use pip
# Actually, let's use a simpler approach for the implementation plan: standard pip install
# We'll just copy pyproject.toml and install from it using pip (modern pip supports pyproject.toml)

# Stage 2: Runtime
FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies (e.g. libpq for psycopg2)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .

# Install dependencies
# Note: For llama-cpp-python with CPU support, we might need specific flags or pre-built wheels
# This basic install assumes standard CPU support
RUN pip install --no-cache-dir .

COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
