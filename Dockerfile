# =============================================================================
# Dockerfile — Ambient Weather MCP Server
# =============================================================================
# Multi-stage build. Builder installs deps with uv; runtime is a clean slim
# image with only the venv and source code. No uv, no build tools, no apt
# cache in the final image.
#
# BUILD:
#   docker build -t ambient-weather-mcp .
#
# RUN (stdio — note the -i flag is required):
#   docker run -i --rm \
#     -e AMBIENT_API_KEY="..." \
#     -e AMBIENT_APP_KEY="..." \
#     ambient-weather-mcp
# =============================================================================

# ---------- Stage 1: builder ----------
FROM python:3.11-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

# uv from official image — only lives in builder stage
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Dependency + metadata layer (cached unless these files change)
# README.md is included because pyproject.toml's readme field references it
# and hatchling validates this during the build.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

# Source layer
COPY src/ ./src/
RUN uv sync --frozen --no-dev

# ---------- Stage 2: runtime ----------
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# OCI labels — populate Docker Hub, GHCR, mcp.so scrapers
LABEL org.opencontainers.image.title="ambient-weather-mcp" \
      org.opencontainers.image.description="MCP server exposing Ambient Weather personal station data to AI assistants" \
      org.opencontainers.image.source="https://github.com/NanaGyamfiPrempeh30/ambient-weather-mcp" \
      org.opencontainers.image.documentation="https://github.com/NanaGyamfiPrempeh30/ambient-weather-mcp#readme" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.authors="Yaw Nana Gyamfi Prempeh"

# Non-root user with fixed UID for Kubernetes runAsNonRoot policies
RUN useradd --create-home --uid 10001 appuser

WORKDIR /app

# Copy venv and source from builder, owned by appuser
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app/src /app/src

USER appuser

# stdio MCP — JSON-RPC on stdin/stdout, logs to stderr.
# No HEALTHCHECK: stdio servers are short-lived per-session.
ENTRYPOINT ["python", "-m", "ambient_weather_mcp"]
CMD []
