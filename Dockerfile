FROM python:3.12-slim

# Install system dependencies and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container
COPY . /app

# Set working directory
WORKDIR /app

# Create and activate virtual environment, then install dependencies
RUN python -m venv .venv && \
    . .venv/bin/activate && \
    uv sync --frozen --no-cache

# Run the application
CMD [".venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]