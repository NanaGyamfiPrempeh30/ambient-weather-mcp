# =============================================================================
# Dockerfile - Ambient Weather MCP Server
# =============================================================================
#
# Uses uv for dependency management (replaces pip).
# uv is faster, more reliable, and produces reproducible installs
# via the uv.lock file.
#
# BUILD:
#   docker build -t ambient-weather-mcp .
#
# RUN:
#   docker run -i --rm \
#     -e AMBIENT_API_KEY="your-key" \
#     -e AMBIENT_APP_KEY="your-app-key" \
#     ambient-weather-mcp

FROM python:3.13-slim

# --- Environment variables ---
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# --- Install uv ---
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# --- Set working directory ---
WORKDIR /app

# --- Install dependencies first (Docker layer caching) ---
# Copy only dependency files first. If pyproject.toml and uv.lock
# haven't changed, Docker reuses the cached install layer.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# --- Copy source code ---
COPY src/ ./src/

# --- Security: run as non-root user ---
RUN useradd --create-home appuser
USER appuser

# --- Entry point ---
CMD ["uv", "run", "python", "-m", "src"]
