"""
server.py - Ambient Weather MCP Server
========================================

HOW MCP WORKS:
--------------
1. An MCP "server" exposes "tools" — functions that an AI can call.
2. An MCP "client" (Claude Desktop, VS Code, Kiro) discovers these tools.
3. When the AI decides to use a tool, the client sends a JSON-RPC message
   to this server via stdin.
4. This server runs the tool function and writes the result to stdout.
5. The client reads the result and the AI presents it in natural language.

Communication: stdin/stdout using JSON-RPC (a standard for remote function calls).
That's why we call it "stdio" mode.

WHAT THIS FILE DOES (Phase 2):
-------------------------------
- Creates a FastMCP server (think of it like creating a Flask/FastAPI app)
- Defines ONE tool: "ping" — just returns "pong" to prove the server works
- Reads API keys from environment variables (validates they exist)
- Starts the server in stdio mode

We'll add real weather tools in Phase 3.

HOW TO RUN:
-----------
  python -m src
"""

import os
import sys
import logging

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


# -------------------------------------------------------------------------
# Step 1: Load configuration
# -------------------------------------------------------------------------

# load_dotenv() reads the .env file (if it exists) and sets the values
# as environment variables. This is only useful during local development.
# When running in Docker, env vars are passed via the -e flag instead.
load_dotenv()

# Configure logging to stderr (NOT stdout).
# Why stderr? Because stdout is reserved for MCP JSON-RPC messages.
# If we print logs to stdout, the MCP client would try to parse them
# as JSON and crash. Stderr is safe for human-readable log output.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("ambient-weather-mcp")


# -------------------------------------------------------------------------
# Step 2: Read and validate API keys
# -------------------------------------------------------------------------

# We read these now but won't USE them until Phase 3 (weather API calls).
# For now we just check they're present so we catch config errors early.
AMBIENT_API_KEY = os.getenv("AMBIENT_API_KEY", "")
AMBIENT_APP_KEY = os.getenv("AMBIENT_APP_KEY", "")

if not AMBIENT_API_KEY:
    logger.warning(
        "AMBIENT_API_KEY is not set. Weather tools will not work. "
        "Get your key at https://dashboard.ambientweather.net/account"
    )

if not AMBIENT_APP_KEY:
    logger.warning(
        "AMBIENT_APP_KEY is not set. Weather tools will not work. "
        "Get your key at https://dashboard.ambientweather.net/account"
    )


# -------------------------------------------------------------------------
# Step 3: Create the MCP server
# -------------------------------------------------------------------------

# FastMCP is like Flask() or FastAPI() — it creates the server instance.
# - name: Shows up in the client's server list (e.g., Claude Desktop settings)
# - description: Helps the AI understand what this server is for
mcp = FastMCP(
    name="ambient-weather",
    instructions=(
        "Access real-time and historical data from Ambient Weather "
        "personal weather stations."
    ),
)


# -------------------------------------------------------------------------
# Step 4: Define tools
# -------------------------------------------------------------------------

# The @mcp.tool() decorator registers a function as an MCP tool.
# Three things matter:
#   1. The function NAME becomes the tool name the AI sees
#   2. The DOCSTRING becomes the tool description (tells the AI when to use it)
#   3. The RETURN VALUE (must be a string) is what the AI receives back


@mcp.tool()
async def ping() -> str:
    """Check if the Ambient Weather MCP server is running and responsive.

    Returns a simple confirmation message. Use this to verify the
    server connection is working before making weather data requests.
    """
    logger.info("Ping tool called")

    # Also report whether API keys are configured
    api_key_status = "configured" if AMBIENT_API_KEY else "MISSING"
    app_key_status = "configured" if AMBIENT_APP_KEY else "MISSING"

    return (
        f"Ambient Weather MCP server is running.\n"
        f"API Key: {api_key_status}\n"
        f"Application Key: {app_key_status}"
    )


# -------------------------------------------------------------------------
# Step 5: Entry point
# -------------------------------------------------------------------------

def main():
    """Start the MCP server in stdio mode.

    stdio mode means the server reads JSON-RPC requests from stdin
    and writes responses to stdout. The MCP client (Claude Desktop,
    VS Code, etc.) manages the process — it starts this script,
    writes to its stdin, and reads from its stdout.

    You don't call this server from a browser like a web server.
    The MCP client handles everything.
    """
    logger.info("Starting Ambient Weather MCP server (stdio mode)...")
    mcp.run(transport="stdio")


# This block runs when you execute the file directly:
#   python src/server.py
if __name__ == "__main__":
    main()
