# Security

## Reporting a vulnerability

Please open a GitHub issue marked `[security]` or contact the maintainer
directly via the email on the GitHub profile. Do not include exploit
details in public issues.

## How this server handles credentials

The server reads `AMBIENT_API_KEY` and `AMBIENT_APP_KEY` from one of two
sources, in order:

1. **OS keyring** (for local development) — credentials are stored via
   the system keychain (macOS Keychain, Windows Credential Manager, or
   Linux Secret Service).
2. **Environment variables** (fallback, and the only path available
   inside Docker containers) — set `AMBIENT_API_KEY` and `AMBIENT_APP_KEY`.

Credentials are never written to disk by this server, never logged, and
never transmitted anywhere except `rt.ambientweather.net` over HTTPS.
The server logs to stderr only; stdout is reserved for JSON-RPC.

## Container security

The Docker image runs as a non-root user (UID 10001) and contains no
embedded secrets. `.env` files are excluded via `.dockerignore`. Linux
containers do not have OS keyring access, so containerized deployments
must use environment variables.

## Supply-chain protections

- Dependencies are pinned via `uv.lock`. Reproducible builds via
  `uv sync --frozen`.
- TruffleHog scans every commit (pre-commit hook) and every push
  (GitHub Actions) for accidentally committed secrets.
- No third-party MCP servers are bundled or proxied through this server.

## Threat model — what this server is NOT

- Not a multi-tenant service. One process, one set of credentials.
- Not authenticated at the MCP layer. Anyone who can speak stdio to the
  process can call its tools. Run it locally or behind your own auth.
- Not rate-limit-aware beyond the built-in 60s response cache. Heavy
  concurrent use will hit Ambient Weather's published rate limits.
