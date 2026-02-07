# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies
# --frozen: strict adherence to uv.lock
# --no-install-project: only install dependencies, not the project itself (since it's a script based project)
RUN uv sync --frozen --no-install-project --no-dev

# Copy application code
COPY . .

# Run the application
# Using ENTRYPOINT allows passing arguments (like --clean-topics or --configure)
# when running the container
ENTRYPOINT ["uv", "run", "python", "main.py"]
