# =============================================================================
# Dockerfile - Ambient Weather MCP Server
# =============================================================================
#
# WHAT THIS DOES:
# Takes a clean Python image, installs our dependencies, copies our code,
# and sets the entry command. The result is a portable container that
# runs the MCP server identically on any machine with Docker.
#
# WHY python:3.12-slim (not alpine):
# Alpine uses musl libc instead of glibc. Some Python packages with
# C extensions break silently on Alpine. Slim is ~120MB vs ~50MB,
# but avoids cryptic segfaults. Worth the tradeoff.
#
# BUILD:
#   docker build -t ambient-weather-mcp .
#
# RUN:
#   docker run -i --rm \
#     -e AMBIENT_API_KEY="your-key" \
#     -e AMBIENT_APP_KEY="your-app-key" \
#     ambient-weather-mcp

FROM python:3.12-slim

# --- Environment variables that affect Python behavior ---

# PYTHONUNBUFFERED=1: Forces Python to flush stdout/stderr immediately.
# Critical for MCP stdio mode — without this, JSON-RPC responses get
# buffered and the MCP client times out waiting for a reply.
ENV PYTHONUNBUFFERED=1

# PYTHONDONTWRITEBYTECODE=1: Don't create __pycache__/.pyc files.
# Saves a few MB in the image and there's no benefit inside a container.
ENV PYTHONDONTWRITEBYTECODE=1

# --- Set working directory ---
WORKDIR /app

# --- Install dependencies first (Docker layer caching) ---
# By copying requirements.txt BEFORE the source code, Docker can
# cache the pip install layer. If you change server.py but not
# requirements.txt, Docker skips the pip install on rebuild.
# This saves significant time during development.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy source code ---
COPY src/ ./src/

# --- Security: run as non-root user ---
# If the container were compromised, the attacker would have limited
# permissions. The MCP server doesn't need root for anything.
RUN useradd --create-home appuser
USER appuser

# --- Entry point ---
# "python -m src" runs src/__main__.py which calls server.main()
# The server starts in stdio mode (reads JSON-RPC from stdin,
# writes responses to stdout).
CMD ["python", "-m", "src"]
